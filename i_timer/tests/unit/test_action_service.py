"""Unit tests for action service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.services import action_service
from app.schemas.timer_schemas import TimerActionResponse
from app.models.timer_models import Timer, TimerStep
from app.services.timer_state import TimerState, TimerStatus, TimerStepData


class TestActionService:
    """Test cases for action service functions."""

    @pytest.mark.asyncio
    async def test_get_actions(self):
        """Test getting the list of actions."""
        actions = await action_service.get_actions()
        
        # Should return list of action values
        assert isinstance(actions, list)
        assert len(actions) > 0
        assert all(isinstance(action, str) for action in actions)

    @pytest.mark.asyncio
    async def test_start_timer_success(self, db_session: AsyncSession):
        """Test starting a timer successfully."""
        # Create mock timer with steps
        mock_timer = MagicMock(spec=Timer)
        mock_timer.steps = [
            MagicMock(spec=TimerStep, duration_seconds=60, repetitions=2),
            MagicMock(spec=TimerStep, duration_seconds=120, repetitions=1)
        ]
        
        # Mock database execute and scalar_one_or_none
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_timer
        db_session.execute = AsyncMock(return_value=mock_result)
        
        # Mock timer manager
        mock_timer_state = MagicMock(spec=TimerState)
        mock_timer_state.time_in_step = 30
        mock_timer_state.time_in_timer = 30
        mock_timer_state.total_duration = 240
        mock_timer_state.status = TimerStatus.RUNNING
        
        with patch('app.services.action_service.timer_manager') as mock_manager:
            mock_manager.start_timer.return_value = mock_timer_state
            
            result = await action_service.start_timer(db_session, 1)
            
            # Verify database call
            db_session.execute.assert_called_once()
            
            # Verify timer manager call
            mock_manager.start_timer.assert_called_once()
            call_args = mock_manager.start_timer.call_args
            assert call_args[0][0] == 1  # timer_id
            assert len(call_args[0][1]) == 2  # steps
            
            # Verify response
            assert isinstance(result, TimerActionResponse)
            assert result.message == "Timer started"
            assert result.time_in_step == 30
            assert result.time_in_timer == 30
            assert result.total_time == 240
            assert result.state == "running"

    @pytest.mark.asyncio
    async def test_start_timer_not_found(self, db_session: AsyncSession):
        """Test starting a timer that doesn't exist."""
        # Mock database execute to return None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        db_session.execute = AsyncMock(return_value=mock_result)
        
        with pytest.raises(HTTPException) as exc_info:
            await action_service.start_timer(db_session, 999)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Timer not found"

    @pytest.mark.asyncio
    async def test_pause_timer_success(self):
        """Test pausing a timer successfully."""
        # Mock timer manager
        mock_timer_state = MagicMock(spec=TimerState)
        mock_timer_state.time_in_step = 45
        mock_timer_state.time_in_timer = 45
        mock_timer_state.total_duration = 240
        mock_timer_state.status = TimerStatus.PAUSED
        
        with patch('app.services.action_service.timer_manager') as mock_manager:
            mock_manager.pause_timer.return_value = mock_timer_state
            
            result = await action_service.pause_timer(1)
            
            # Verify timer manager call
            mock_manager.pause_timer.assert_called_once_with(1)
            
            # Verify response
            assert isinstance(result, TimerActionResponse)
            assert result.message == "Timer paused"
            assert result.time_in_step == 45
            assert result.time_in_timer == 45
            assert result.total_time == 240
            assert result.state == "paused"

    @pytest.mark.asyncio
    async def test_pause_timer_not_found(self):
        """Test pausing a timer that doesn't exist."""
        with patch('app.services.action_service.timer_manager') as mock_manager:
            mock_manager.pause_timer.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await action_service.pause_timer(999)
            
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Timer not found or not running"

    @pytest.mark.asyncio
    async def test_resume_timer_success(self):
        """Test resuming a timer successfully."""
        # Mock timer manager
        mock_timer_state = MagicMock(spec=TimerState)
        mock_timer_state.time_in_step = 30
        mock_timer_state.time_in_timer = 30
        mock_timer_state.total_duration = 240
        mock_timer_state.status = TimerStatus.RUNNING
        
        with patch('app.services.action_service.timer_manager') as mock_manager:
            mock_manager.resume_timer.return_value = mock_timer_state
            
            result = await action_service.resume_timer(1)
            
            # Verify timer manager call
            mock_manager.resume_timer.assert_called_once_with(1)
            
            # Verify response
            assert isinstance(result, TimerActionResponse)
            assert result.message == "Timer resumed"
            assert result.time_in_step == 30
            assert result.time_in_timer == 30
            assert result.total_time == 240
            assert result.state == "running"

    @pytest.mark.asyncio
    async def test_resume_timer_not_found(self):
        """Test resuming a timer that doesn't exist."""
        with patch('app.services.action_service.timer_manager') as mock_manager:
            mock_manager.resume_timer.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await action_service.resume_timer(999)
            
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Timer not found or not paused"

    @pytest.mark.asyncio
    async def test_stop_timer_success(self):
        """Test stopping a timer successfully."""
        # Mock timer manager
        mock_timer_state = MagicMock(spec=TimerState)
        mock_timer_state.time_in_step = 60
        mock_timer_state.time_in_timer = 60
        mock_timer_state.total_duration = 240
        mock_timer_state.status = TimerStatus.STOPPED
        
        with patch('app.services.action_service.timer_manager') as mock_manager:
            mock_manager.stop_timer.return_value = mock_timer_state
            
            result = await action_service.stop_timer(1)
            
            # Verify timer manager call
            mock_manager.stop_timer.assert_called_once_with(1)
            
            # Verify response
            assert isinstance(result, TimerActionResponse)
            assert result.message == "Timer stopped"
            assert result.time_in_step == 60
            assert result.time_in_timer == 60
            assert result.total_time == 240
            assert result.state == "stopped"

    @pytest.mark.asyncio
    async def test_stop_timer_not_found(self):
        """Test stopping a timer that doesn't exist."""
        with patch('app.services.action_service.timer_manager') as mock_manager:
            mock_manager.stop_timer.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await action_service.stop_timer(999)
            
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Timer not found"

    @pytest.mark.asyncio
    async def test_get_timer_status_success(self):
        """Test getting timer status successfully."""
        # Mock timer manager
        mock_timer_state = MagicMock(spec=TimerState)
        mock_timer_state.time_in_step = 30
        mock_timer_state.time_in_timer = 90
        mock_timer_state.total_duration = 240
        mock_timer_state.status = TimerStatus.RUNNING
        
        with patch('app.services.action_service.timer_manager') as mock_manager:
            mock_manager.get_timer_state.return_value = mock_timer_state
            
            result = await action_service.get_timer_status(1)
            
            # Verify timer manager call
            mock_manager.get_timer_state.assert_called_once_with(1)
            
            # Verify response
            assert isinstance(result, TimerActionResponse)
            assert result.message == "Timer status retrieved"
            assert result.time_in_step == 30
            assert result.time_in_timer == 90
            assert result.total_time == 240
            assert result.state == "running"

    @pytest.mark.asyncio
    async def test_get_timer_status_not_found(self):
        """Test getting status of a timer that doesn't exist."""
        with patch('app.services.action_service.timer_manager') as mock_manager:
            mock_manager.get_timer_state.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await action_service.get_timer_status(999)
            
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Timer not found"

    @pytest.mark.asyncio
    async def test_start_timer_with_empty_steps(self, db_session: AsyncSession):
        """Test starting a timer with no steps."""
        # Create mock timer with no steps
        mock_timer = MagicMock(spec=Timer)
        mock_timer.steps = []
        
        # Mock database execute and scalar_one_or_none
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_timer
        db_session.execute = AsyncMock(return_value=mock_result)
        
        # Mock timer manager
        mock_timer_state = MagicMock(spec=TimerState)
        mock_timer_state.time_in_step = 0
        mock_timer_state.time_in_timer = 0
        mock_timer_state.total_duration = 0
        mock_timer_state.status = TimerStatus.RUNNING
        
        with patch('app.services.action_service.timer_manager') as mock_manager:
            mock_manager.start_timer.return_value = mock_timer_state
            
            result = await action_service.start_timer(db_session, 1)
            
            # Verify timer manager call with empty steps
            mock_manager.start_timer.assert_called_once_with(1, [])
            
            # Verify response
            assert result.time_in_step == 0
            assert result.time_in_timer == 0
            assert result.total_time == 0

    @pytest.mark.asyncio
    async def test_start_timer_with_multiple_steps(self, db_session: AsyncSession):
        """Test starting a timer with multiple steps."""
        # Create mock timer with multiple steps
        mock_timer = MagicMock(spec=Timer)
        mock_timer.steps = [
            MagicMock(spec=TimerStep, duration_seconds=60, repetitions=2),
            MagicMock(spec=TimerStep, duration_seconds=120, repetitions=1),
            MagicMock(spec=TimerStep, duration_seconds=90, repetitions=3)
        ]
        
        # Mock database execute and scalar_one_or_none
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_timer
        db_session.execute = AsyncMock(return_value=mock_result)
        
        # Mock timer manager
        mock_timer_state = MagicMock(spec=TimerState)
        mock_timer_state.time_in_step = 30
        mock_timer_state.time_in_timer = 30
        mock_timer_state.total_duration = 510  # 60*2 + 120*1 + 90*3
        mock_timer_state.status = TimerStatus.RUNNING
        
        with patch('app.services.action_service.timer_manager') as mock_manager:
            mock_manager.start_timer.return_value = mock_timer_state
            
            result = await action_service.start_timer(db_session, 1)
            
            # Verify timer manager call with correct steps
            call_args = mock_manager.start_timer.call_args
            steps = call_args[0][1]
            assert len(steps) == 3
            assert steps[0].step_index == 0
            assert steps[0].duration_seconds == 60
            assert steps[0].repetitions == 2
            assert steps[1].step_index == 1
            assert steps[1].duration_seconds == 120
            assert steps[1].repetitions == 1
            assert steps[2].step_index == 2
            assert steps[2].duration_seconds == 90
            assert steps[2].repetitions == 3
            
            # Verify response
            assert result.total_time == 510

    @pytest.mark.asyncio
    async def test_all_timer_states(self):
        """Test all timer states in responses."""
        states_to_test = [
            (TimerStatus.RUNNING, "running"),
            (TimerStatus.PAUSED, "paused"),
            (TimerStatus.STOPPED, "stopped"),
            (TimerStatus.FINISHED, "finished")
        ]
        
        for status, expected_state in states_to_test:
            mock_timer_state = MagicMock(spec=TimerState)
            mock_timer_state.time_in_step = 30
            mock_timer_state.time_in_timer = 30
            mock_timer_state.total_duration = 240
            mock_timer_state.status = status
            
            with patch('app.services.action_service.timer_manager') as mock_manager:
                mock_manager.get_timer_state.return_value = mock_timer_state
                
                result = await action_service.get_timer_status(1)
                
                assert result.state == expected_state 