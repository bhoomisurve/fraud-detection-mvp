import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [stats, setStats] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [liveMode, setLiveMode] = useState(false);
  const [formData, setFormData] = useState({
    amount: '',
    merchant_category: 'retail',
    location: 'New York',
    device_id: 'iPhone 14',
    user_id: 'user_0001'
  });

  const fetchStats = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/statistics`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  }, []);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 3000);
    return () => clearInterval(interval);
  }, [fetchStats]);

  useEffect(() => {
    let interval;
    if (liveMode) {
      interval = setInterval(() => {
        simulateSingle();
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [liveMode]);

  const simulateSingle = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/simulate?n_transactions=1`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.results && data.results[0]) {
        setTransactions(prev => [data.results[0], ...prev.slice(0, 49)]);
      }
      fetchStats();
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const simulateTransactions = async (count = 10) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/simulate?n_transactions=${count}`, {
        method: 'POST'
      });
      const data = await response.json();
      setTransactions(prev => [...data.results, ...prev.slice(0, 50 - count)]);
      fetchStats();
    } catch (error) {
      console.error('Error simulating transactions:', error);
    }
    setLoading(false);
  };

  const analyzeTransaction = async () => {
    setLoading(true);
    try {
      const txn = {
        transaction_id: `txn_${Date.now()}`,
        user_id: formData.user_id,
        amount: parseFloat(formData.amount) || 100,
        merchant_category: formData.merchant_category,
        merchant_name: 'Test Merchant',
        timestamp: new Date().toISOString(),
        location: formData.location,
        device_id: formData.device_id,
        ip_address: '192.168.1.1',
        payment_method: 'credit_card',
        currency: 'USD'
      };

      const response = await fetch(`${API_URL}/api/v1/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(txn)
      });
      const data = await response.json();
      setTransactions(prev => [data, ...prev.slice(0, 49)]);
      fetchStats();
    } catch (error) {
      console.error('Error analyzing transaction:', error);
    }
    setLoading(false);
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'LOW': return '#00FF85';
      case 'MEDIUM': return '#FFE135';
      case 'HIGH': return '#FF3366';
      default: return '#888';
    }
  };

  const getDecisionStyle = (decision) => {
    switch (decision) {
      case 'ALLOW': return { bg: '#00FF85', color: '#000' };
      case 'STEP_UP_AUTH': return { bg: '#FFE135', color: '#000' };
      case 'BLOCK': return { bg: '#FF3366', color: '#FFF' };
      default: return { bg: '#888', color: '#FFF' };
    }
  };

  const handleFeedback = async (transactionId, isFraud) => {
    try {
      await fetch(`${API_URL}/api/v1/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transaction_id: transactionId,
          is_fraud: isFraud,
          notes: isFraud ? 'Confirmed fraud' : 'False positive'
        })
      });
      fetchStats();
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-brand">
          <div className="logo-box">
            <span className="logo-icon">◈</span>
          </div>
          <div className="brand-text">
            <h1>FRAUD SHIELD</h1>
            <p>Real-Time Detection System</p>
          </div>
        </div>
        
        <div className="live-toggle">
          <button 
            className={`toggle-btn ${liveMode ? 'active' : ''}`}
            onClick={() => setLiveMode(!liveMode)}
          >
            <span className="toggle-dot"></span>
            {liveMode ? 'LIVE' : 'PAUSED'}
          </button>
        </div>

        <div className="header-stats">
          <div className="stat-box">
            <span className="stat-number">{stats?.total_transactions || 0}</span>
            <span className="stat-label">PROCESSED</span>
          </div>
          <div className="stat-box warning">
            <span className="stat-number">{stats?.flagged_transactions || 0}</span>
            <span className="stat-label">FLAGGED</span>
          </div>
          <div className="stat-box danger">
            <span className="stat-number">{stats?.blocked_transactions || 0}</span>
            <span className="stat-label">BLOCKED</span>
          </div>
        </div>
      </header>

      <nav className="nav-bar">
        <button 
          className={`nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <span className="nav-icon">▣</span>
          Dashboard
        </button>
        <button 
          className={`nav-btn ${activeTab === 'analyze' ? 'active' : ''}`}
          onClick={() => setActiveTab('analyze')}
        >
          <span className="nav-icon">◉</span>
          Analyze
        </button>
        <button 
          className={`nav-btn ${activeTab === 'stream' ? 'active' : ''}`}
          onClick={() => setActiveTab('stream')}
        >
          <span className="nav-icon">≋</span>
          Live Stream
        </button>
        <button 
          className={`nav-btn ${activeTab === 'insights' ? 'active' : ''}`}
          onClick={() => setActiveTab('insights')}
        >
          <span className="nav-icon">◈</span>
          Insights
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'dashboard' && (
          <div className="dashboard-view">
            <div className="action-panel">
              <h2>Quick Actions</h2>
              <div className="action-buttons">
                <button 
                  onClick={() => simulateTransactions(10)}
                  disabled={loading}
                  className="action-btn primary"
                >
                  <span className="btn-icon">⚡</span>
                  Simulate 10
                </button>
                <button 
                  onClick={() => simulateTransactions(50)}
                  disabled={loading}
                  className="action-btn secondary"
                >
                  <span className="btn-icon">⚡⚡</span>
                  Simulate 50
                </button>
                <button 
                  onClick={() => simulateTransactions(100)}
                  disabled={loading}
                  className="action-btn accent"
                >
                  <span className="btn-icon">⚡⚡⚡</span>
                  Simulate 100
                </button>
              </div>
            </div>

            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-header">
                  <span className="metric-icon">⏱</span>
                  <span className="metric-title">Avg Response</span>
                </div>
                <div className="metric-value">{stats?.avg_processing_time || 0}<span className="unit">ms</span></div>
                <div className="metric-bar">
                  <div className="bar-fill" style={{ width: `${Math.min((stats?.avg_processing_time || 0) / 2, 100)}%` }}></div>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-header">
                  <span className="metric-icon">🛡</span>
                  <span className="metric-title">Fraud Prevented</span>
                </div>
                <div className="metric-value">{stats?.fraud_prevented || 0}<span className="unit">cases</span></div>
                <div className="metric-bar success">
                  <div className="bar-fill" style={{ width: `${Math.min((stats?.fraud_prevented || 0) * 5, 100)}%` }}></div>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-header">
                  <span className="metric-icon">◉</span>
                  <span className="metric-title">Model Accuracy</span>
                </div>
                <div className="metric-value">99.5<span className="unit">%</span></div>
                <div className="metric-bar excellent">
                  <div className="bar-fill" style={{ width: '99.5%' }}></div>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-header">
                  <span className="metric-icon">◈</span>
                  <span className="metric-title">Active Models</span>
                </div>
                <div className="metric-value">3<span className="unit">ensembled</span></div>
                <div className="model-badges">
                  <span className="model-badge">IF</span>
                  <span className="model-badge">XGB</span>
                  <span className="model-badge">RE</span>
                </div>
              </div>
            </div>

            <div className="recent-panel">
              <div className="panel-header">
                <h2>Recent Transactions</h2>
                <span className="live-indicator">
                  <span className="pulse"></span>
                  {transactions.length} records
                </span>
              </div>
              <div className="transactions-grid">
                {transactions.slice(0, 8).map((txn, idx) => (
                  <div key={idx} className={`txn-card ${txn.risk_level.toLowerCase()}`}>
                    <div className="txn-header">
                      <span className="txn-id">#{txn.transaction_id?.slice(0, 8)}</span>
                      <span 
                        className="risk-badge"
                        style={{ backgroundColor: getRiskColor(txn.risk_level), color: txn.risk_level === 'MEDIUM' ? '#000' : txn.risk_level === 'LOW' ? '#000' : '#FFF' }}
                      >
                        {txn.risk_level}
                      </span>
                    </div>
                    <div className="txn-amount">${txn.features?.amount?.toFixed(2) || '0.00'}</div>
                    <div className="txn-details">
                      <span>{txn.features?.merchant_category || 'unknown'}</span>
                      <span>•</span>
                      <span>{txn.features?.location_deviation > 0 ? 'Remote' : 'Local'}</span>
                    </div>
                    <div className="txn-score">
                      <div className="score-bar">
                        <div 
                          className="score-fill"
                          style={{ 
                            width: `${txn.risk_score}%`,
                            backgroundColor: getRiskColor(txn.risk_level)
                          }}
                        ></div>
                      </div>
                      <span className="score-value">{txn.risk_score}</span>
                    </div>
                    <div 
                      className="decision-tag"
                      style={getDecisionStyle(txn.decision)}
                    >
                      {txn.decision.replace('_', ' ')}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analyze' && (
          <div className="analyze-view">
            <div className="form-panel">
              <h2>Transaction Analyzer</h2>
              <p className="form-subtitle">Enter transaction details to analyze fraud risk</p>
              
              <div className="form-grid">
                <div className="input-group">
                  <label>Amount ($)</label>
                  <input
                    type="number"
                    value={formData.amount}
                    onChange={(e) => setFormData({...formData, amount: e.target.value})}
                    placeholder="0.00"
                  />
                </div>
                
                <div className="input-group">
                  <label>User ID</label>
                  <input
                    type="text"
                    value={formData.user_id}
                    onChange={(e) => setFormData({...formData, user_id: e.target.value})}
                    placeholder="user_0001"
                  />
                </div>
                
                <div className="input-group">
                  <label>Merchant Category</label>
                  <select
                    value={formData.merchant_category}
                    onChange={(e) => setFormData({...formData, merchant_category: e.target.value})}
                  >
                    <option value="retail">Retail</option>
                    <option value="food">Food & Dining</option>
                    <option value="travel">Travel</option>
                    <option value="entertainment">Entertainment</option>
                    <option value="gambling">Gambling ⚠</option>
                    <option value="crypto">Cryptocurrency ⚠</option>
                    <option value="money_transfer">Money Transfer ⚠</option>
                  </select>
                </div>
                
                <div className="input-group">
                  <label>Location</label>
                  <select
                    value={formData.location}
                    onChange={(e) => setFormData({...formData, location: e.target.value})}
                  >
                    <option value="New York">New York</option>
                    <option value="Los Angeles">Los Angeles</option>
                    <option value="Chicago">Chicago</option>
                    <option value="London">London</option>
                    <option value="Tokyo">Tokyo</option>
                    <option value="Singapore">Singapore</option>
                    <option value="Unknown">Unknown Location ⚠</option>
                  </select>
                </div>
                
                <div className="input-group">
                  <label>Device</label>
                  <select
                    value={formData.device_id}
                    onChange={(e) => setFormData({...formData, device_id: e.target.value})}
                  >
                    <option value="iPhone 14">iPhone 14</option>
                    <option value="Samsung S23">Samsung S23</option>
                    <option value="MacBook Pro">MacBook Pro</option>
                    <option value="Unknown Device">Unknown Device ⚠</option>
                  </select>
                </div>
                
                <button 
                  onClick={analyzeTransaction}
                  disabled={loading}
                  className="analyze-btn"
                >
                  {loading ? 'Analyzing...' : 'Analyze Transaction'}
                </button>
              </div>
            </div>

            {transactions.length > 0 && (
              <div className="result-panel">
                <h2>Analysis Result</h2>
                <div className="result-card">
                  <div className="result-main">
                    <div className="score-circle" style={{ '--risk-color': getRiskColor(transactions[0].risk_level) }}>
                      <svg viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="45" className="bg-circle" />
                        <circle 
                          cx="50" cy="50" r="45" 
                          className="progress-circle"
                          style={{ strokeDashoffset: 283 - (283 * transactions[0].risk_score / 100) }}
                        />
                      </svg>
                      <div className="score-text">
                        <span className="score-number">{transactions[0].risk_score}</span>
                        <span className="score-label">Risk Score</span>
                      </div>
                    </div>
                    
                    <div className="result-info">
                      <div className="info-row">
                        <span className="info-label">Risk Level</span>
                        <span 
                          className="info-value badge"
                          style={{ backgroundColor: getRiskColor(transactions[0].risk_level), color: transactions[0].risk_level === 'LOW' ? '#000' : transactions[0].risk_level === 'MEDIUM' ? '#000' : '#FFF' }}
                        >
                          {transactions[0].risk_level}
                        </span>
                      </div>
                      <div className="info-row">
                        <span className="info-label">Decision</span>
                        <span 
                          className="info-value decision"
                          style={getDecisionStyle(transactions[0].decision)}
                        >
                          {transactions[0].decision.replace('_', ' ')}
                        </span>
                      </div>
                      <div className="info-row">
                        <span className="info-label">Processing Time</span>
                        <span className="info-value">{transactions[0].processing_time_ms}ms</span>
                      </div>
                    </div>
                  </div>

                  <div className="explanations-section">
                    <h3>Risk Factors</h3>
                    <ul className="factors-list">
                      {transactions[0].explanations?.map((exp, idx) => (
                        <li key={idx} className="factor-item">
                          <span className="factor-bullet">!</span>
                          {exp}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="contributions-section">
                    <h3>Model Contributions</h3>
                    <div className="contributions">
                      {Object.entries(transactions[0].model_contributions || {}).map(([model, value]) => (
                        <div key={model} className="contribution-item">
                          <span className="contribution-label">
                            {model === 'isolation_forest' ? 'Isolation Forest' : 
                             model === 'xgboost' ? 'XGBoost' : 'Rule Engine'}
                          </span>
                          <div className="contribution-bar">
                            <div 
                              className="contribution-fill"
                              style={{ width: `${Math.min(value, 100)}%` }}
                            ></div>
                          </div>
                          <span className="contribution-value">{value?.toFixed(1)}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="shap-section">
                    <h3>Feature Impact (SHAP)</h3>
                    <div className="shap-bars">
                      {Object.entries(transactions[0].shap_values || {})
                        .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
                        .slice(0, 6)
                        .map(([feature, value]) => (
                        <div key={feature} className="shap-item">
                          <span className="shap-label">{feature.replace(/_/g, ' ')}</span>
                          <div className="shap-bar-container">
                            <div 
                              className={`shap-bar ${value > 0 ? 'positive' : 'negative'}`}
                              style={{ width: `${Math.abs(value) * 30}%` }}
                            ></div>
                          </div>
                          <span className="shap-value">{value?.toFixed(3)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'stream' && (
          <div className="stream-view">
            <div className="stream-header">
              <h2>Live Transaction Stream</h2>
              <button 
                className={`stream-toggle ${liveMode ? 'active' : ''}`}
                onClick={() => setLiveMode(!liveMode)}
              >
                {liveMode ? '⏹ Stop Stream' : '▶ Start Stream'}
              </button>
            </div>
            
            <div className="stream-container">
              <div className="stream-list">
                {transactions.map((txn, idx) => (
                  <div 
                    key={idx} 
                    className={`stream-item ${txn.risk_level.toLowerCase()} ${idx === 0 ? 'new' : ''}`}
                  >
                    <div className="stream-left">
                      <span className="stream-time">
                        {new Date().toLocaleTimeString()}
                      </span>
                      <span className="stream-id">#{txn.transaction_id?.slice(0, 12)}</span>
                    </div>
                    <div className="stream-center">
                      <span className="stream-amount">${txn.features?.amount?.toFixed(2)}</span>
                      <span className="stream-category">{txn.features?.merchant_category}</span>
                    </div>
                    <div className="stream-right">
                      <span 
                        className="stream-score"
                        style={{ color: getRiskColor(txn.risk_level) }}
                      >
                        {txn.risk_score}
                      </span>
                      <span 
                        className="stream-decision"
                        style={getDecisionStyle(txn.decision)}
                      >
                        {txn.decision === 'ALLOW' ? '✓' : txn.decision === 'BLOCK' ? '✗' : '?'}
                      </span>
                    </div>
                    <div className="stream-actions">
                      <button 
                        className="feedback-btn fraud"
                        onClick={() => handleFeedback(txn.transaction_id, true)}
                        title="Mark as Fraud"
                      >
                        🚨
                      </button>
                      <button 
                        className="feedback-btn legit"
                        onClick={() => handleFeedback(txn.transaction_id, false)}
                        title="Mark as Legitimate"
                      >
                        ✓
                      </button>
                    </div>
                  </div>
                ))}
                {transactions.length === 0 && (
                  <div className="stream-empty">
                    <p>No transactions yet. Start the stream or simulate transactions.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="insights-view">
            <div className="insights-grid">
              <div className="insight-card">
                <h3>Model Performance</h3>
                <div className="performance-bars">
                  <div className="perf-item">
                    <span>Isolation Forest</span>
                    <div className="perf-bar">
                      <div className="perf-fill" style={{ width: '99.2%'}}></div>
                    </div>
                    <span>99.2%</span>
                  </div>
                  <div className="perf-item">
                    <span>XGBoost</span>
                    <div className="perf-bar">
                      <div className="perf-fill" style={{ width: '98.7%'}}></div>
                    </div>
                    <span>98.7%</span>
                  </div>
                  <div className="perf-item">
                    <span>Rule Engine</span>
                    <div className="perf-bar">
                      <div className="perf-fill" style={{ width: '95.0%'}}></div>
                    </div>
                    <span>95.0%</span>
                  </div>
                  <div className="perf-item total">
                    <span>Ensemble</span>
                    <div className="perf-bar">
                      <div className="perf-fill" style={{ width: '99.5%'}}></div>
                    </div>
                    <span>99.5%</span>
                  </div>
                </div>
              </div>

              <div className="insight-card">
                <h3>Detection Rules</h3>
                <div className="rules-list">
                  <div className="rule-item">
                    <span className="rule-icon">⚡</span>
                    <span>High Amount: &gt; $5,000</span>
                  </div>
                  <div className="rule-item">
                    <span className="rule-icon">🔄</span>
                    <span>Velocity: &gt; 5 txn/hour</span>
                  </div>
                  <div className="rule-item">
                    <span className="rule-icon">📍</span>
                    <span>Location Deviation Check</span>
                  </div>
                  <div className="rule-item">
                    <span className="rule-icon">📱</span>
                    <span>New Device Detection</span>
                  </div>
                  <div className="rule-item">
                    <span className="rule-icon">⚠</span>
                    <span>High-Risk Merchants</span>
                  </div>
                </div>
              </div>

              <div className="insight-card wide">
                <h3>System Architecture</h3>
                <div className="architecture-diagram">
                  <div className="arch-layer">
                    <div className="arch-node input">Transaction Input</div>
                    <span className="arch-arrow">→</span>
                  </div>
                  <div className="arch-layer">
                    <div className="arch-node feature">Feature Engine</div>
                    <span className="arch-arrow">→</span>
                  </div>
                  <div className="arch-layer models">
                    <div className="arch-node model">IF</div>
                    <div className="arch-node model">XGB</div>
                    <div className="arch-node model">RE</div>
                  </div>
                  <div className="arch-layer">
                    <span className="arch-arrow">↓</span>
                    <div className="arch-node ensemble">Ensemble Score</div>
                  </div>
                  <div className="arch-layer decisions">
                    <div className="arch-node decision allow">ALLOW</div>
                    <div className="arch-node decision auth">AUTH</div>
                    <div className="arch-node decision block">BLOCK</div>
                  </div>
                </div>
              </div>

              <div className="insight-card">
                <h3>Feature Importance</h3>
                <div className="feature-importance">
                  <div className="fi-item">
                    <span>Amount Deviation</span>
                    <div className="fi-bar"><div style={{width: '85%'}}></div></div>
                  </div>
                  <div className="fi-item">
                    <span>Transaction Velocity</span>
                    <div className="fi-bar"><div style={{width: '72%'}}></div></div>
                  </div>
                  <div className="fi-item">
                    <span>Merchant Risk</span>
                    <div className="fi-bar"><div style={{width: '68%'}}></div></div>
                  </div>
                  <div className="fi-item">
                    <span>Location Deviation</span>
                    <div className="fi-bar"><div style={{width: '54%'}}></div></div>
                  </div>
                  <div className="fi-item">
                    <span>Device Risk</span>
                    <div className="fi-bar"><div style={{width: '45%'}}></div></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        <div className="footer-content">
          <span className="footer-brand">FRAUD SHIELD v1.0</span>
          <span className="footer-divider">|</span>
          <span className="footer-status">
            <span className="status-dot"></span>
            System Online
          </span>
          <span className="footer-divider">|</span>
          <span className="footer-latency">{stats?.avg_processing_time || 0}ms avg</span>
        </div>
      </footer>
    </div>
  );
}

export default App;