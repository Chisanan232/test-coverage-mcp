import React, { useState } from 'react';
import styles from './Feedback.module.css';

export default function Feedback(): JSX.Element {
  const [feedback, setFeedback] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!feedback.trim()) {
      setError('Please enter your feedback');
      return;
    }

    try {
      // Submit feedback to GitHub Issues
      const issueBody = `## Documentation Feedback\n\n${feedback}\n\n---\n_Submitted from documentation site_`;
      const url = `https://github.com/Chisanan232/test-coverage-mcp/issues/new?title=Documentation%20Feedback&body=${encodeURIComponent(issueBody)}`;
      window.open(url, '_blank');
      
      setFeedback('');
      setSubmitted(true);
      setTimeout(() => setSubmitted(false), 3000);
    } catch (err) {
      setError('Failed to submit feedback. Please try again.');
    }
  };

  return (
    <div className={styles.feedbackContainer}>
      <h3>📝 Documentation Feedback</h3>
      <p>Help us improve the documentation</p>
      
      <form onSubmit={handleSubmit}>
        <textarea
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          placeholder="Share your feedback, suggestions, or report issues..."
          rows={4}
          className={styles.textarea}
        />
        
        {error && <div className={styles.error}>{error}</div>}
        {submitted && <div className={styles.success}>✅ Thank you for your feedback!</div>}
        
        <button type="submit" className={styles.submitButton}>
          Submit Feedback
        </button>
      </form>
    </div>
  );
}
