"""Unit tests for timer state management."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from freezegun import freeze_time

from app.services.timer_state import (
    TimerStateManager,
    TimerState,
    TimerStepData,
    TimerStatus
)


class TestTimerStateManager:
    """Test cases for TimerStateManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = TimerStateManager()
        self.sample_steps = [
            TimerStepData(step_index=0, duration_seconds=60, repetitions=2),
            TimerStepData(step_index=1, duration_seconds=120, repetitions=1)
        ]

    def test_init(self):
        """Test TimerStateManager initialization."""
        manager = TimerStateManager()
        assert manager._timers == {}
        assert manager._tasks == {}

    def test_calculate_total_duration(self):
        """Test total duration calculation."""
        steps = [
            TimerStepData(step_index=0, duration_seconds=60, repetitions=2),
            TimerStepData(step_index=1, duration_seconds=120, repetitions=1)
        ]
        total_duration = self.manager._calculate_total_duration(steps)
        assert total_duration == (60 * 2) + (120 * 1) == 240

    def test_calculate_total_duration_empty_steps(self):
        """Test total duration calculation with empty steps."""
        total_duration = self.manager._calculate_total_duration([])
        assert total_duration == 0

    @freeze_time("2024-01-01 12:00:00")
    def test_start_timer(self):
        """Test starting a new timer."""
        timer_id = 1
        state = self.manager.start_timer(timer_id, self.sample_steps)
        
        assert state.timer_id == timer_id
        assert state.status == TimerStatus.RUNNING
        assert state.steps == self.sample_steps
        assert state.current_step_index == 0
        assert state.current_repetition == 1
        assert state.time_in_step == 0
        assert state.time_in_timer == 0
        assert state.start_time == datetime(2024, 1, 1, 12, 0, 0)
        assert state.pause_time is None
        assert state.total_time_paused == timedelta(0)
        assert state.total_duration == 240
        assert timer_id in self.manager._timers

    def test_start_timer_overwrites_existing(self):
        """Test that starting a timer overwrites existing timer with same ID."""
        timer_id = 1
        initial_state = self.manager.start_timer(timer_id, self.sample_steps)
        
        # Start timer again with different steps
        new_steps = [TimerStepData(step_index=0, duration_seconds=30, repetitions=1)]
        new_state = self.manager.start_timer(timer_id, new_steps)
        
        assert new_state.timer_id == timer_id
        assert new_state.steps == new_steps
        assert new_state.total_duration == 30
        assert len(self.manager._timers) == 1

    def test_get_timer_state_not_found(self):
        """Test getting state of non-existent timer."""
        state = self.manager.get_timer_state(999)
        assert state is None

    @freeze_time("2024-01-01 12:00:00")
    def test_get_timer_state_running(self):
        """Test getting state of running timer."""
        timer_id = 1
        self.manager.start_timer(timer_id, self.sample_steps)
        
        with freeze_time("2024-01-01 12:00:30"):  # 30 seconds later
            state = self.manager.get_timer_state(timer_id)
            
            assert state is not None
            assert state.timer_id == timer_id
            assert state.status == TimerStatus.RUNNING
            assert state.time_in_timer == 30
            assert state.current_step_index == 0
            assert state.current_repetition == 1
            assert state.time_in_step == 30

    @freeze_time("2024-01-01 12:00:00")
    def test_get_timer_state_finished(self):
        """Test getting state of finished timer."""
        timer_id = 1
        self.manager.start_timer(timer_id, self.sample_steps)
        
        with freeze_time("2024-01-01 12:04:00"):  # 4 minutes later (past total duration)
            state = self.manager.get_timer_state(timer_id)
            
            assert state is not None
            assert state.status == TimerStatus.FINISHED
            assert state.current_step_index == 1  # Last step
            assert state.current_repetition == 1
            assert state.time_in_step == 120

    def test_is_timer_running_not_found(self):
        """Test checking if non-existent timer is running."""
        is_running = self.manager.is_timer_running(999)
        assert is_running is False

    def test_is_timer_running_true(self):
        """Test checking if timer is running."""
        timer_id = 1
        self.manager.start_timer(timer_id, self.sample_steps)
        
        is_running = self.manager.is_timer_running(timer_id)
        assert is_running is True

    def test_is_timer_running_false_when_paused(self):
        """Test checking if paused timer is running."""
        timer_id = 1
        self.manager.start_timer(timer_id, self.sample_steps)
        self.manager.pause_timer(timer_id)
        
        is_running = self.manager.is_timer_running(timer_id)
        assert is_running is False

    def test_pause_timer_not_found(self):
        """Test pausing non-existent timer."""
        state = self.manager.pause_timer(999)
        assert state is None

    @freeze_time("2024-01-01 12:00:00")
    def test_pause_timer_success(self):
        """Test pausing a running timer."""
        timer_id = 1
        self.manager.start_timer(timer_id, self.sample_steps)
        
        with freeze_time("2024-01-01 12:00:30"):
            state = self.manager.pause_timer(timer_id)
            
            assert state is not None
            assert state.status == TimerStatus.PAUSED
            assert state.pause_time == datetime(2024, 1, 1, 12, 0, 30)

    def test_pause_timer_already_paused(self):
        """Test pausing an already paused timer."""
        timer_id = 1
        self.manager.start_timer(timer_id, self.sample_steps)
        self.manager.pause_timer(timer_id)

        # Try to pause again - should fail
        state = self.manager.pause_timer(timer_id)
        assert state is None  # Cannot pause an already paused timer

    def test_resume_timer_not_found(self):
        """Test resuming non-existent timer."""
        state = self.manager.resume_timer(999)
        assert state is None

    @freeze_time("2024-01-01 12:00:00")
    def test_resume_timer_success(self):
        """Test resuming a paused timer."""
        timer_id = 1
        self.manager.start_timer(timer_id, self.sample_steps)
        
        with freeze_time("2024-01-01 12:00:30"):
            self.manager.pause_timer(timer_id)
        
        with freeze_time("2024-01-01 12:00:45"):
            state = self.manager.resume_timer(timer_id)
            
            assert state is not None
            assert state.status == TimerStatus.RUNNING
            assert state.pause_time is None
            assert state.total_time_paused == timedelta(seconds=15)

    def test_resume_timer_not_paused(self):
        """Test resuming a timer that's not paused."""
        timer_id = 1
        self.manager.start_timer(timer_id, self.sample_steps)

        # Try to resume running timer - should fail
        state = self.manager.resume_timer(timer_id)
        assert state is None  # Cannot resume a timer that's not paused

    def test_stop_timer_not_found(self):
        """Test stopping non-existent timer."""
        state = self.manager.stop_timer(999)
        assert state is None

    def test_stop_timer_success(self):
        """Test stopping a timer."""
        timer_id = 1
        self.manager.start_timer(timer_id, self.sample_steps)
        
        state = self.manager.stop_timer(timer_id)
        
        assert state is not None
        assert state.status == TimerStatus.STOPPED

    def test_remove_timer_not_found(self):
        """Test removing non-existent timer."""
        # Should not raise any exceptions
        self.manager.remove_timer(999)

    def test_remove_timer_success(self):
        """Test removing a timer."""
        timer_id = 1
        self.manager.start_timer(timer_id, self.sample_steps)
        
        # Mock task for this timer
        mock_task = MagicMock()
        self.manager._tasks[timer_id] = mock_task
        
        self.manager.remove_timer(timer_id)
        
        assert timer_id not in self.manager._timers
        assert timer_id not in self.manager._tasks
        mock_task.cancel.assert_called_once()

    @freeze_time("2024-01-01 12:00:00")
    def test_update_timer_state_advances_through_steps(self):
        """Test that timer state correctly advances through steps."""
        timer_id = 1
        steps = [
            TimerStepData(step_index=0, duration_seconds=60, repetitions=2),
            TimerStepData(step_index=1, duration_seconds=120, repetitions=1)
        ]
        self.manager.start_timer(timer_id, steps)
        
        # After 90 seconds (1.5 minutes), should be in second repetition of first step
        with freeze_time("2024-01-01 12:01:30"):
            state = self.manager.get_timer_state(timer_id)
            assert state.current_step_index == 0
            assert state.current_repetition == 2
            assert state.time_in_step == 30
        
        # After 120 seconds (2 minutes), should be in second step
        with freeze_time("2024-01-01 12:02:00"):
            state = self.manager.get_timer_state(timer_id)
            assert state.current_step_index == 1
            assert state.current_repetition == 1
            assert state.time_in_step == 0

    @freeze_time("2024-01-01 12:00:00")
    def test_update_timer_state_with_pause(self):
        """Test timer state update accounting for pause time."""
        timer_id = 1
        self.manager.start_timer(timer_id, self.sample_steps)
        
        # Run for 30 seconds
        with freeze_time("2024-01-01 12:00:30"):
            self.manager.pause_timer(timer_id)
        
        # Wait 60 seconds while paused
        with freeze_time("2024-01-01 12:01:30"):
            self.manager.resume_timer(timer_id)
            
            # Check state after resume (should still be at 30 seconds elapsed)
            state = self.manager.get_timer_state(timer_id)
            assert state.time_in_timer == 30
            assert state.current_step_index == 0
            assert state.current_repetition == 1
            assert state.time_in_step == 30

    def test_update_timer_state_not_found(self):
        """Test updating state of non-existent timer."""
        # Should not raise any exceptions
        self.manager._update_timer_state(999)

    @freeze_time("2024-01-01 12:00:00")
    def test_complex_timer_sequence(self):
        """Test a complex sequence of timer operations."""
        timer_id = 1
        steps = [
            TimerStepData(step_index=0, duration_seconds=30, repetitions=2),
            TimerStepData(step_index=1, duration_seconds=60, repetitions=1)
        ]
        
        # Start timer
        state = self.manager.start_timer(timer_id, steps)
        assert state.status == TimerStatus.RUNNING
        
        # Run for 45 seconds
        with freeze_time("2024-01-01 12:00:45"):
            state = self.manager.get_timer_state(timer_id)
            assert state.current_step_index == 0
            assert state.current_repetition == 2
            assert state.time_in_step == 15
        
        # Pause timer
        with freeze_time("2024-01-01 12:00:50"):
            state = self.manager.pause_timer(timer_id)
            assert state.status == TimerStatus.PAUSED
        
        # Wait 30 seconds while paused
        with freeze_time("2024-01-01 12:01:20"):
            state = self.manager.resume_timer(timer_id)
            assert state.status == TimerStatus.RUNNING
            
            # Check state after resume (should still be at 50 seconds elapsed)
            state = self.manager.get_timer_state(timer_id)
            assert state.time_in_timer == 50
            assert state.current_step_index == 0
            assert state.current_repetition == 2
            assert state.time_in_step == 20
        
        # Stop timer
        state = self.manager.stop_timer(timer_id)
        assert state.status == TimerStatus.STOPPED
        
        # Remove timer
        self.manager.remove_timer(timer_id)
        assert timer_id not in self.manager._timers 