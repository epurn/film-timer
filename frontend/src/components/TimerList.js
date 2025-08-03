import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Alert, Spinner } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import ApiService from '../services/api';

const TimerList = () => {
  const [timers, setTimers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTimers = async () => {
      try {
        setLoading(true);
        const data = await ApiService.getTimers();
        setTimers(data);
      } catch (err) {
        setError('Failed to load timers. Please check if the backend is running.');
        console.error('Error fetching timers:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTimers();
  }, []);

  const handleTimerClick = (timerId) => {
    navigate(`/timer/${timerId}`);
  };

  if (loading) {
    return (
      <div className="text-center">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <p className="mt-2">Loading timers...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error</Alert.Heading>
        {error}
      </Alert>
    );
  }

  return (
    <div>
      <h1 className="mb-4">My Timers</h1>
      
      {timers.length === 0 ? (
        <Alert variant="info">
          <Alert.Heading>No Timers Found</Alert.Heading>
          <p>You don't have any timers yet. Create one using the API to get started!</p>
        </Alert>
      ) : (
        <Row>
          {timers.map((timer) => (
            <Col key={timer.id} xs={12} md={6} lg={4} className="mb-3">
              <Card 
                className="h-100 timer-card" 
                style={{ cursor: 'pointer' }}
                onClick={() => handleTimerClick(timer.id)}
              >
                <Card.Body>
                  <Card.Title>{timer.name}</Card.Title>
                  <Card.Text>
                    {timer.description || 'No description available'}
                  </Card.Text>
                  <small className="text-muted">
                    {timer.steps?.length || 0} step{timer.steps?.length !== 1 ? 's' : ''}
                  </small>
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
};

export default TimerList;