import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TextField, Button, Grid, Container, Paper, Typography } from '@mui/material';
import CampgroundList from './CampgroundList';

function App() {
  const [availability, setAvailability] = useState({
    start_window_date: '',
    end_window_date: '',
    num_nights: '',
    days_of_the_week: '',
  });

  const [filters, setFilters] = useState({
    rating: '',
    number_of_ratings: '',
    location: { center: [null, null], radius: '' }, // Initialize with empty coordinates
  });

  const [campgrounds, setCampgrounds] = useState([]);
  const [errors, setErrors] = useState({});
  const [locationEnabled, setLocationEnabled] = useState(false);

  // Use browser's Geolocation API to get user's location
  useEffect(() => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFilters((prevFilters) => ({
            ...prevFilters,
            location: {
              ...prevFilters.location,
              center: [position.coords.latitude, position.coords.longitude],
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

  // Function to handle user input for availability
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setAvailability({ ...availability, [name]: value });
  };

  // Function to handle filter input changes
  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters({ ...filters, [name]: value });
  };

  // Validate the fields when user clicks 'Search'
  const validateFields = () => {
    const newErrors = {};

    if (!filters.rating || isNaN(filters.rating) || parseFloat(filters.rating) <= 0) {
      newErrors.rating = 'Minimum rating must be a positive number';
    }

    if (!filters.number_of_ratings || isNaN(filters.number_of_ratings) || parseInt(filters.number_of_ratings) <= 0) {
      newErrors.number_of_ratings = 'Number of ratings must be a positive integer';
    }

    if (!filters.location.radius || isNaN(filters.location.radius) || parseFloat(filters.location.radius) <= 0) {
      newErrors.radius = 'Location radius must be a positive number';
    }

    if (!availability.num_nights || isNaN(availability.num_nights) || parseInt(availability.num_nights) <= 0) {
      newErrors.num_nights = 'Number of nights must be a positive integer';
    }

    setErrors(newErrors);

    return Object.keys(newErrors).length === 0;
  };

  // Function to handle the search
  const handleSearch = async () => {
    if (!validateFields()) {
      return;
    }

    if (!locationEnabled || filters.location.center[0] === null || filters.location.center[1] === null) {
      alert('Could not get your location. Please make sure location services are enabled.');
      return;
    }

    const requestData = {
      availability: {
        start_window_date: availability.start_window_date,
        end_window_date: availability.end_window_date,
        num_nights: parseInt(availability.num_nights),
        days_of_the_week: availability.days_of_the_week.split(',').map(Number),
      },
      filters: {
        AND: [
          { 'rating.average_rating': { gt: parseFloat(filters.rating) } },
          { 'rating.number_of_ratings': { gt: parseInt(filters.number_of_ratings) } },
          {
            location: {
              within_radius: {
                center: filters.location.center, // This now holds the user's location
                radius: parseFloat(filters.location.radius),
              },
            },
          },
        ],
      },
      sort: {
        key: 'rating.average_rating',
        reverse: true,
      },
    };

    try {
      const response = await axios.post('http://127.0.0.1:8000/filter-campgrounds', requestData);
      setCampgrounds(response.data);
    } catch (error) {
      console.error('Error fetching campgrounds:', error);
    }
  };

  return (
    <Container>
      <Paper elevation={3} style={{ padding: '20px', marginTop: '20px' }}>
        <Typography variant="h4" gutterBottom>
          Find Campgrounds
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              label="Start Date"
              type="date"
              name="start_window_date"
              value={availability.start_window_date}
              onChange={handleInputChange}
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              label="End Date"
              type="date"
              name="end_window_date"
              value={availability.end_window_date}
              onChange={handleInputChange}
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              label="Number of Nights"
              name="num_nights"
              value={availability.num_nights}
              onChange={handleInputChange}
              fullWidth
              error={!!errors.num_nights}
              helperText={errors.num_nights}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              label="Days of the Week (e.g., 4,5)"
              name="days_of_the_week"
              value={availability.days_of_the_week}
              onChange={handleInputChange}
              fullWidth
            />
          </Grid>

          {/* Filters */}
          <Grid item xs={12} md={6}>
            <TextField
              label="Minimum Rating (e.g., 3.5)"
              name="rating"
              value={filters.rating}
              onChange={handleFilterChange}
              fullWidth
              error={!!errors.rating}
              helperText={errors.rating}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              label="Number of Ratings (e.g., 200)"
              name="number_of_ratings"
              value={filters.number_of_ratings}
              onChange={handleFilterChange}
              fullWidth
              error={!!errors.number_of_ratings}
              helperText={errors.number_of_ratings}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              label="Location Radius (in miles)"
              name="radius"
              value={filters.location.radius}
              onChange={(e) =>
                setFilters({
                  ...filters,
                  location: {
                    ...filters.location,
                    radius: e.target.value,
                  },
                })
              }
              fullWidth
              error={!!errors.radius}
              helperText={errors.radius}
            />
          </Grid>

          <Grid item xs={12}>
            <Button variant="contained" color="primary" onClick={handleSearch} fullWidth>
              Search Campgrounds
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {campgrounds.length > 0 && (
        <Paper elevation={3} style={{ padding: '20px', marginTop: '20px' }}>
          <CampgroundList campgrounds={campgrounds} />
        </Paper>
      )}
    </Container>
  );
}

export default App;

