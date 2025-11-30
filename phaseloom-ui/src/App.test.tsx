import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import App from './App';
import { fetchSessions } from './api';
import type { SessionInfo } from './api';

// Mock the entire api module
vi.mock('./api');

describe('App', () => {
  it('renders the App component and displays sessions', async () => {
    // Arrange: a mock session list
    const mockSessions: SessionInfo[] = [
      { session_id: 'session-123', path: 'path/to/session' },
      { session_id: 'session-456', path: 'path/to/another/session' },
    ];
    // Arrange: mock the fetchSessions implementation
    vi.mocked(fetchSessions).mockResolvedValue(mockSessions);

    // Act: render the component
    render(<App />);

    // Assert: Check that the sessions are displayed
    // Use findByText for async operations
    expect(await screen.findByText('session-123')).toBeInTheDocument();
    expect(await screen.findByText('session-456')).toBeInTheDocument();
  });

  it('shows an error message when fetching sessions fails', async () => {
    // Arrange: mock the fetchSessions implementation to reject
    vi.mocked(fetchSessions).mockRejectedValue(new Error('Failed to fetch'));

    // Act
    render(<App />);

    // Assert
    expect(await screen.findByText(/Error loading sessions/i)).toBeInTheDocument();
  });
});
