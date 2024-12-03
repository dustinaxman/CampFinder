import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button, Container, Paper, Typography } from '@mui/material';
import CampgroundList from './CampgroundList';
import QueryFilterForm from './QueryFilterForm';
import './App.css';

function App() {
  const [query, setQuery] = useState({
    filters: { AND: [], OR: [], location: { center: [null, null], radius: '' } },
    sort: { key: 'rating.average_rating', reverse: true },
  });

  const [campgrounds, setCampgrounds] = useState([]);
  const [errors, setErrors] = useState({});
  const [isSearching, setIsSearching] = useState(false);
  const [locationEnabled, setLocationEnabled] = useState(false);

  // Use browser's Geolocation API to get user's location
  useEffect(() => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setQuery((prevQuery) => ({
            ...prevQuery,
            filters: {
              ...prevQuery.filters,
              location: {
                ...prevQuery.filters.location,
                center: [position.coords.latitude, position.coords.longitude],
              },
            },
          }));
          setLocationEnabled(true);
        },
        (error) => {
          console.error('Error getting location:', error);
          setLocationEnabled(false);
        }
      );
    } else {
      console.error('Geolocation not available in this browser.');
      setLocationEnabled(false);
    }
  }, []);

  // Validate query structure
  const validateQuery = () => {
    const newErrors = {};

    if (query.sort && !query.sort.key) {
      newErrors.sort = 'Sort key is required.';
    }

    if (!query.filters.location.radius || isNaN(query.filters.location.radius)) {
      newErrors.locationRadius = 'Valid location radius is required.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle search submission
  const handleSearch = async () => {
    if (!validateQuery()) return;

    if (!locationEnabled || query.filters.location.center.includes(null)) {
      alert('Location is required. Please enable location services.');
      return;
    }

    setIsSearching(true);
    try {
      const response = await axios.post('http://127.0.0.1:8000/filter-campgrounds', query);
      setCampgrounds(response.data);
    } catch (error) {
      console.error('Error fetching campgrounds:', error);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <Container>
      <Paper elevation={3} className="main-container">
        <Typography variant="h4" gutterBottom>
          Find Campgrounds
        </Typography>
        <QueryFilterForm query={query} setQuery={setQuery} errors={errors} />
        <Button
          variant="contained"
          color="primary"
          onClick={handleSearch}
          fullWidth
          disabled={isSearching}
        >
          {isSearching ? 'Searching...' : 'Search Campgrounds'}
        </Button>
      </Paper>

      {campgrounds.length > 0 && (
        <Paper elevation={3} className="result-container">
          <CampgroundList campgrounds={campgrounds} />
        </Paper>
      )}
    </Container>
  );
}

export default App;
