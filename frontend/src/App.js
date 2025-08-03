import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import NavigationBar from './components/NavigationBar';
import TimerList from './components/TimerList';
import TimerDetail from './components/TimerDetail';
import './App.css';

const App = () => {
  return (
    <div className="App">
      <NavigationBar />
      <Container className="mt-4">
        <Routes>
          <Route path="/" element={<TimerList />} />
          <Route path="/timer/:id" element={<TimerDetail />} />
        </Routes>
      </Container>
    </div>
  );
};

export default App;