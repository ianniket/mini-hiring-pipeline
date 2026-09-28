import React, { useState, useEffect } from 'react';
import { Search, Plus, X, Clock, User, CheckCircle2, XCircle } from 'lucide-react';

const STAGES = ['Applied', 'Screening', 'Interview', 'Offer', 'Hired'];

export default function App() {
  const [candidates, setCandidates] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchError, setSearchError] = useState('');
  
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newCandidateName, setNewCandidateName] = useState('');
  
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  useEffect(() => {
    fetchCandidates();
  }, []);

  const fetchCandidates = async () => {
    try {
      const res = await fetch('/api/candidates');
      if (res.ok) {
        const data = await res.json();
        setCandidates(data);
        setSearchError('');
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSearch = async (e) => {
    const q = e.target.value;
    setSearchQuery(q);
    
    if (!q.trim()) {
      fetchCandidates();
      setSearchError('');
      return;
    }
    
    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      if (data.error) {
        setSearchError(data.error);
        setCandidates([]);
      } else {
        setSearchError('');
        setCandidates(data.results);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleAddCandidate = async (e) => {
    e.preventDefault();
    if (!newCandidateName.trim()) return;
    
    try {
      const res = await fetch('/api/candidates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newCandidateName })
      });
      if (res.ok) {
        setNewCandidateName('');
        setIsAddModalOpen(false);
        fetchCandidates();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const moveCandidate = async (id, newStage) => {
    try {
      const res = await fetch(`/api/candidates/${id}/stage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ new_stage: newStage })
      });
      if (res.ok) {
        const updated = await res.json();
        if (selectedCandidate && selectedCandidate.id === id) {
          setSelectedCandidate(updated);
        }
        
        if (searchQuery.trim()) {
          // Trigger search again to update list
          handleSearch({ target: { value: searchQuery } });
        } else {
          fetchCandidates();
        }
      } else {
        const err = await res.json();
        alert(err.detail);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const openCandidateModal = async (id) => {
    try {
      const res = await fetch(`/api/candidates/${id}`);
      if (res.ok) {
        setSelectedCandidate(await res.json());
      }
    } catch (e) {
      console.error(e);
    }
  };

  const groupedCandidates = STAGES.reduce((acc, stage) => {
    acc[stage] = candidates.filter(c => c.current_stage === stage && c.status !== 'Rejected');
    return acc;
  }, {});
  
  // Also keep rejected ones separated or show them? We'll put them in a pseudo-stage if searched,
  // but normally they're hidden from the main pipeline view.
  const rejectedCandidates = candidates.filter(c => c.status === 'Rejected');

  return (
    <div className="app-container">
      <header className="header glass">
        <h1 className="title">Pipeline</h1>
        
        <div className="search-container">
          <Search className="search-icon" size={18} />
          <input 
            type="text" 
            className="search-input" 
            placeholder="Search candidates (e.g. 'Who is in Interview?', 'stuck in Screening for 2 days')"
            value={searchQuery}
            onChange={handleSearch}
          />
        </div>
        
        <button className="btn-primary" onClick={() => setIsAddModalOpen(true)}>
          <Plus size={18} />
          Add Candidate
        </button>
      </header>

      {searchError && (
        <div className="search-error">
          {searchError}
        </div>
      )}

      <div className="board">
        {STAGES.map(stage => (
          <div key={stage} className="column glass-panel">
            <div className="column-header">
              <span className="column-title">{stage}</span>
              <span className="badge">{groupedCandidates[stage]?.length || 0}</span>
            </div>
            
            <div className="cards-container">
              {groupedCandidates[stage]?.map(c => (
                <div key={c.id} className="candidate-card glass" onClick={() => openCandidateModal(c.id)}>
                  <div className="card-bg-glow" style={{'--stage-color': `var(--stage-${stage.toLowerCase()})`}}></div>
                  <div className="card-header">
                    <span className="candidate-name">{c.name}</span>
                  </div>
                  <div className="card-footer">
                    <span className="time-in-stage">
                      <Clock size={12} />
                      {c.time_in_stage}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
        
        {/* If we searched and found rejected, show them in their own pseudo-column if there are any */}
        {rejectedCandidates.length > 0 && searchQuery.trim() !== '' && (
          <div className="column glass-panel" style={{opacity: 0.8}}>
            <div className="column-header">
              <span className="column-title" style={{color: 'var(--stage-rejected)'}}>Rejected</span>
              <span className="badge">{rejectedCandidates.length}</span>
            </div>
            <div className="cards-container">
              {rejectedCandidates.map(c => (
                <div key={c.id} className="candidate-card glass" onClick={() => openCandidateModal(c.id)}>
                  <div className="card-header">
                    <span className="candidate-name">{c.name}</span>
                    <span className="candidate-status status-Rejected">Rejected</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Add Modal */}
      {isAddModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content glass">
            <button className="modal-close" onClick={() => setIsAddModalOpen(false)}>
              <X size={24} />
            </button>
            <h2>Add New Candidate</h2>
            <form onSubmit={handleAddCandidate}>
              <div className="form-group" style={{marginTop: '1.5rem'}}>
                <label className="form-label">Full Name</label>
                <input 
                  type="text" 
                  className="form-input" 
                  value={newCandidateName}
                  onChange={(e) => setNewCandidateName(e.target.value)}
                  autoFocus
                  required
                />
              </div>
              <div className="actions">
                <button type="submit" className="btn-primary">Add to Pipeline</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {selectedCandidate && (
        <div className="modal-overlay">
          <div className="modal-content glass">
            <button className="modal-close" onClick={() => setSelectedCandidate(null)}>
              <X size={24} />
            </button>
            
            <div style={{display: 'flex', alignItems: 'center', gap: '1rem'}}>
              <h2>{selectedCandidate.name}</h2>
              <span className={`candidate-status status-${selectedCandidate.status}`}>
                {selectedCandidate.status}
              </span>
            </div>
            
            <p style={{color: 'var(--text-secondary)', marginTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
              <Clock size={14} /> Currently in <strong>{selectedCandidate.current_stage}</strong> for {selectedCandidate.time_in_stage}
            </p>

            <div className="stage-actions">
              {/* Generate next stage button if possible */}
              {selectedCandidate.status === 'Active' && (
                <>
                  {STAGES.indexOf(selectedCandidate.current_stage) < STAGES.length - 1 && (
                    <button 
                      className="btn-stage"
                      onClick={() => moveCandidate(selectedCandidate.id, STAGES[STAGES.indexOf(selectedCandidate.current_stage) + 1])}
                    >
                      Move to {STAGES[STAGES.indexOf(selectedCandidate.current_stage) + 1]}
                    </button>
                  )}
                  {STAGES.indexOf(selectedCandidate.current_stage) === STAGES.length - 2 && (
                    <button 
                      className="btn-stage" style={{borderColor: 'var(--stage-hired)', color: 'var(--stage-hired)'}}
                      onClick={() => moveCandidate(selectedCandidate.id, 'Hired')}
                    >
                      <CheckCircle2 size={16} style={{display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom'}}/>
                      Hire Candidate
                    </button>
                  )}
                  <button 
                    className="btn-stage btn-reject"
                    onClick={() => moveCandidate(selectedCandidate.id, 'Rejected')}
                  >
                    <XCircle size={16} style={{display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom'}}/>
                    Reject
                  </button>
                </>
              )}
            </div>

            <h3 style={{marginTop: '2rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem'}}>Audit History</h3>
            <div className="timeline">
              {selectedCandidate.history.map((h, i) => (
                <div key={i} className="timeline-item">
                  <div className="timeline-dot"></div>
                  <div className="timeline-content">
                    <div style={{fontWeight: 500}}>{h.stage}</div>
                    <div style={{fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.3rem'}}>
                      {new Date(h.timestamp).toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
          </div>
        </div>
      )}
    </div>
  );
}
