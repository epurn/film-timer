import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Alert, Spinner, ListGroup, Row, Col } from 'react-bootstrap';
import ApiService from '../services/api';

const TimerDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [timer, setTimer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTimer = async () => {
      try {
        setLoading(true);
        const data = await ApiService.getTimer(id);
        setTimer(data);
      } catch (err) {
        setError('Failed to load timer details. Please check if the backend is running.');
        console.error('Error fetching timer:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTimer();
  }, [id]);

  const handleBackToList = () => {
    navigate('/');
  };

  const handlePlay = () => {
    // Placeholder for play functionality
    console.log('Play timer');
  };

  const handlePause = () => {
    // Placeholder for pause functionality
    console.log('Pause timer');
  };

  const handleStop = () => {
    // Placeholder for stop functionality
    console.log('Stop timer');
  };

  const formatDuration = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="text-center">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <p className="mt-2">Loading timer details...</p>
      </div>
    );
  }

  if (error || !timer) {
    return (
      <div>
        <Button variant="secondary" onClick={handleBackToList} className="mb-3">
          ← Back to Timer List
        </Button>
        <Alert variant="danger">
          <Alert.Heading>Error</Alert.Heading>
          {error || 'Timer not found'}
        </Alert>
      </div>
    );
  }

  return (
    <div>
      <Button variant="secondary" onClick={handleBackToList} className="mb-3">
        ← Back to Timer List
      </Button>

      {/* Timer Info */}
      <Card className="mb-4">
        <Card.Header>
          <h2 className="mb-0">{timer.name}</h2>
        </Card.Header>
        <Card.Body>
          {timer.description && (
            <Card.Text>{timer.description}</Card.Text>
          )}
          <small className="text-muted">
            Created: {new Date(timer.created_at).toLocaleDateString()}
          </small>
        </Card.Body>
      </Card>

      {/* Timer Steps */}
      <Card className="mb-4">
        <Card.Header>
          <h4 className="mb-0">Timer Steps ({timer.steps?.length || 0})</h4>
        </Card.Header>
        <Card.Body>
          {timer.steps && timer.steps.length > 0 ? (
            <ListGroup variant="flush">
              {timer.steps
                .sort((a, b) => a.order_index - b.order_index)
                .map((step, index) => (
                  <ListGroup.Item key={step.id} className="px-0">
                    <Row className="align-items-center">
                      <Col xs={1}>
                        <strong>#{index + 1}</strong>
                      </Col>
                      <Col xs={4}>
                        <strong>{step.title}</strong>
                      </Col>
                      <Col xs={3}>
                        <span className="badge bg-primary">
                          {formatDuration(step.duration_seconds)}
                        </span>
                        {step.repetitions > 1 && (
                          <span className="badge bg-secondary ms-2">
                            x{step.repetitions}
                          </span>
                        )}
                      </Col>
                      <Col xs={4}>
                        {step.notes && (
                          <small className="text-muted">
                            {step.notes}
                          </small>
                        )}
                      </Col>
                    </Row>
                  </ListGroup.Item>
                ))}
            </ListGroup>
          ) : (
            <Alert variant="info">
              <Alert.Heading>No Steps</Alert.Heading>
              <p>This timer doesn't have any steps yet.</p>
            </Alert>
          )}
        </Card.Body>
      </Card>

      {/* Timer Controls */}
      <Card>
        <Card.Header>
          <h4 className="mb-0">Timer Controls</h4>
        </Card.Header>
        <Card.Body className="text-center">
          <Button 
            variant="success" 
            size="lg" 
            className="me-3"
            onClick={handlePlay}
          >
            ▶ Play
          </Button>
          <Button 
            variant="warning" 
            size="lg" 
            className="me-3"
            onClick={handlePause}
          >
            ⏸ Pause
          </Button>
          <Button 
            variant="danger" 
            size="lg"
            onClick={handleStop}
          >
            ⏹ Stop
          </Button>
          <div className="mt-3">
            <small className="text-muted">
              Timer controls are not functional yet - this is just the UI scaffold.
            </small>
          </div>
        </Card.Body>
      </Card>
    </div>
  );
};

export default TimerDetail;