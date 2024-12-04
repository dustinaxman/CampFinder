import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button, Container, Paper, Typography, Box, TextField } from '@mui/material';
import QueryFilterForm from './QueryFilterForm';
import CampgroundList from './CampgroundList';
import AvailabilityForm from './AvailabilityForm';
import './App.css';

function App() {
  const [andFilters, setAndFilters] = useState([]);
  const [orFilters, setOrFilters] = useState([]);
  const [weatherFilters, setWeatherFilters] = useState({});
  const [locationFilter, setLocationFilter] = useState({ center: [null, null], radius: '' });
  const [availability, setAvailability] = useState({
    start_window_date: '',
    end_window_date: '',
    num_nights: 2,
    days_of_the_week: [0, 1, 2, 3, 4, 5, 6],
  });
  const [campgrounds, setCampgrounds] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocationFilter((prev) => ({
            ...prev,
            center: [position.coords.latitude, position.coords.longitude],
          }));
        },
        (error) => console.error('Error getting location:', error)
      );
    }
  }, []);

  const handleFilterUpdate = (filters, type) => {
    if (type === 'AND') setAndFilters(filters);
    if (type === 'OR') setOrFilters(filters);
  };

  const handleWeatherFilterUpdate = (newWeatherFilters) => {
    setWeatherFilters(newWeatherFilters);
  };

  const handleAvailabilityUpdate = (newAvailability) => {
    setAvailability(newAvailability);
  };

  const handleSearch = async () => {
    const query = {
      availability,
      filters: {
        weather: weatherFilters,
        AND: andFilters,
        OR: orFilters,
        location: locationFilter,
      },
      sort: {
        key: 'rating.average_rating',
        reverse: true,
      },
    };

    console.log('Query:', query);

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
      <Paper elevation={3} style={{ padding: '16px' }}>
        <Typography variant="h4" gutterBottom>
          Find Campgrounds
        </Typography>

        {/* Availability Filters */}
        <Typography variant="h6">Availability</Typography>
        <AvailabilityForm
          availability={availability}
          onAvailabilityUpdate={handleAvailabilityUpdate}
        />

        {/* AND Filters */}
        <Typography variant="h6" style={{ marginTop: '16px' }}>
          AND Filters
        </Typography>
        <QueryFilterForm
          filterType="AND"
          onFilterUpdate={(filters) => handleFilterUpdate(filters, 'AND')}
        />

        {/* OR Filters */}
        <Typography variant="h6" style={{ marginTop: '16px' }}>
          OR Filters
        </Typography>
        <QueryFilterForm
          filterType="OR"
          onFilterUpdate={(filters) => handleFilterUpdate(filters, 'OR')}
        />

        {/* Weather Filters */}
        <Typography variant="h6" style={{ marginTop: '16px' }}>
          Weather Filters
        </Typography>
        <QueryFilterForm isWeatherFilter onFilterUpdate={handleWeatherFilterUpdate} />

        {/* Location Filters */}
        <Typography variant="h6" style={{ marginTop: '16px' }}>
          Location Filters
        </Typography>
        <TextField
          label="Radius (km)"
          type="number"
          value={locationFilter.radius}
          onChange={(e) =>
            setLocationFilter((prev) => ({ ...prev, radius: parseFloat(e.target.value) || 0 }))
          }
        />
        <Typography>
          Location: Latitude {locationFilter.center[0] || 'N/A'}, Longitude{' '}
          {locationFilter.center[1] || 'N/A'}
        </Typography>

        {/* Search Button */}
        <Button
          variant="contained"
          color="primary"
          onClick={handleSearch}
          fullWidth
          style={{ marginTop: '16px' }}
          disabled={isSearching}
        >
          {isSearching ? 'Searching...' : 'Search Campsites'}
        </Button>
      </Paper>

      {/* Results */}
      {campgrounds.length > 0 && (
        <Paper elevation={3} style={{ marginTop: '16px', padding: '16px' }}>
          <CampgroundList campgrounds={campgrounds} />
        </Paper>
      )}
    </Container>
  );
}

export default App;
