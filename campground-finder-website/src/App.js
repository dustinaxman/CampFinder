import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Button,
  Container,
  Paper,
  Typography,
  Box,
  Checkbox,
  TextField,
  FormControlLabel,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
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
    <Container maxWidth="md" style={{ marginTop: '24px' }}>
      <Paper elevation={3} style={{ padding: '24px' }}>
        <Typography variant="h4" gutterBottom>
          Find Campgrounds
        </Typography>

        {/* Availability Filters */}
        <Box mt={3}>
          <Typography variant="h6" gutterBottom>
            Availability
          </Typography>
          <AvailabilityForm
            availability={availability}
            onAvailabilityUpdate={handleAvailabilityUpdate}
          />
        </Box>

        {/* AND Filters */}
        <Box mt={4}>
          <Typography variant="h6" gutterBottom>
            AND Filters
          </Typography>
          <QueryFilterForm
            filterType="AND"
            onFilterUpdate={(filters) => handleFilterUpdate(filters, 'AND')}
          />
        </Box>

        {/* OR Filters */}
        <Box mt={4}>
          <Typography variant="h6" gutterBottom>
            OR Filters
          </Typography>
          <QueryFilterForm
            filterType="OR"
            onFilterUpdate={(filters) => handleFilterUpdate(filters, 'OR')}
          />
        </Box>

        {/* Weather Filters */}
        <Box mt={4}>
          <Typography variant="h6" gutterBottom>
            Weather Filters
          </Typography>
          <QueryFilterForm isWeatherFilter onFilterUpdate={handleWeatherFilterUpdate} />
        </Box>

        {/* Location Filters */}
        <Box mt={4}>
          <Typography variant="h6" gutterBottom>
            Location Filters
          </Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Radius (Miles)"
                type="number"
                value={locationFilter.radius}
                onChange={(e) =>
                  setLocationFilter((prev) => ({
                    ...prev,
                    radius: parseFloat(e.target.value) || '',
                  }))
                }
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body1">
                Your Location: Latitude {locationFilter.center[0] || 'N/A'}, Longitude{' '}
                {locationFilter.center[1] || 'N/A'}
              </Typography>
            </Grid>
          </Grid>
        </Box>

        {/* Search Button */}
        <Box mt={4}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleSearch}
            fullWidth
            size="large"
            disabled={isSearching}
          >
            {isSearching ? 'Searching...' : 'Search Campsites'}
          </Button>
        </Box>
      </Paper>

      {/* Results */}
      {campgrounds.length > 0 && (
        <Paper elevation={3} style={{ marginTop: '24px', padding: '24px' }}>
          <Typography variant="h5" gutterBottom>
            Search Results
          </Typography>
          <CampgroundList campgrounds={campgrounds} />
        </Paper>
      )}
    </Container>
  );
}

export default App;
