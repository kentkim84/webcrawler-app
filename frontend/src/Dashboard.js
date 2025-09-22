import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import Chart from 'chart.js/auto';

const Dashboard = () => {
  const [logs, setLogs] = useState([]);
  const [health, setHealth] = useState({ cpu: 0, memory: 0 });
  const [ws, setWs] = useState(null);

  useEffect(() => {
    fetchLogs();
    fetchHealth();
    const interval = setInterval(fetchHealth, 5000);

    const websocket = new WebSocket('ws://localhost:8000/pubsub');
    websocket.onopen = () => {
      websocket.send(JSON.stringify({ action: 'subscribe', topic: 'logs' }));
    };
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.topic === 'logs') {
        const logData = data.data;
        const newLog = {
          id: Math.random(), // Temporary ID for frontend
          timestamp: logData.asctime,
          level: logData.levelname,
          message: logData.msg || JSON.stringify(logData),
          user_id: logData.user_id
        };
        setLogs((prev) => [...prev, newLog].slice(-100)); // Keep last 100 logs
      }
    };
    websocket.onclose = () => {
      console.log('WebSocket closed, attempting to reconnect...');
    };
    setWs(websocket);

    return () => {
      clearInterval(interval);
      if (ws) ws.close();
    };
  }, []);

  const fetchLogs = async () => {
    try {
      const response = await axios.get('http://localhost:8000/logs/');
      setLogs(response.data);
    } catch (err) {
      console.error('Failed to fetch logs:', err);
    }
  };

  const fetchHealth = async () => {
    try {
      const response = await axios.get('http://localhost:8000/health');
      setHealth({ cpu: response.data.cpu, memory: response.data.memory });
    } catch (err) {
      console.error('Failed to fetch health:', err);
    }
  };

  const chartData = {
    labels: ['CPU', 'Memory'],
    datasets: [{
      label: 'Usage %',
      data: [health.cpu, health.memory],
      backgroundColor: ['rgba(75, 192, 192, 0.6)', 'rgba(153, 102, 255, 0.6)'],
      borderColor: ['rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)'],
      borderWidth: 1
    }]
  };

  const chartOptions = {
    scales: {
      y: {
        beginAtZero: true,
        max: 100
      }
    },
    plugins: {
      legend: {
        display: true
      }
    }
  };

  const errorLogs = logs.filter(log => log.level === 'ERROR');

  return (
    <div style={{ marginTop: '20px' }}>
      <h2>Monitoring Dashboard</h2>
      <h3>System Health</h3>
      <Bar data={chartData} options={chartOptions} />
      <h3>Job Logs</h3>
      <ul style={{ maxHeight: '300px', overflowY: 'auto' }}>
        {logs.map((log) => (
          <li
            key={log.id}
            style={{
              color: log.level === 'ERROR' ? 'red' : 'black',
              padding: '5px 0'
            }}
          >
            [{log.timestamp}] {log.level}: {log.message}
            {log.user_id ? ` (User: ${log.user_id})` : ''}
          </li>
        ))}
      </ul>
      <h3>Crawl Error Reports</h3>
      <ul style={{ maxHeight: '200px', overflowY: 'auto' }}>
        {errorLogs.map((log) => (
          <li key={log.id} style={{ padding: '5px 0' }}>
            [{log.timestamp}] {log.message}
            {log.user_id ? ` (User: ${log.user_id})` : ''}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Dashboard;