import React from 'react';
import { Typography, Grid, Paper, List, ListItem, ListItemText } from '@mui/material';

function Campground({ campground }) {
  return (
    <Paper elevation={3} style={{ padding: '20px', marginBottom: '20px' }}>
      <Typography variant="h5" gutterBottom>
        {campground.name}
      </Typography>
      <Typography variant="subtitle1" gutterBottom style={{ fontWeight: 'bold' }}>
          ID: <a href={`https://www.recreation.gov/camping/campgrounds/${campground.id}`} target="_blank" rel="noopener noreferrer">
            {campground.id}
          </a>
      </Typography>
      <Typography variant="body1" gutterBottom>
        Average Rating: {campground.rating?.average_rating?.toFixed(2) || 'N/A'} (
        {campground.rating?.number_of_ratings || 0} reviews)
      </Typography>
      <Typography variant="body1" gutterBottom>
        Activities: {campground.activities.join(', ')}
      </Typography>
      <Typography variant="body1" gutterBottom>
        Amenities: {campground.amenities.join(', ')}
      </Typography>
      <Grid container spacing={2}>
        {campground.campsites.map((campsite) => (
          <Grid item xs={12} md={6} key={campsite.campsite_id}>
            <Paper elevation={2} style={{ padding: '10px' }}>
              <Typography variant="h6" gutterBottom>
                  Campsite: {campsite.name} (ID: <a href={`https://www.recreation.gov/camping/campsites/${campsite.campsite_id}`} target="_blank" rel="noopener noreferrer">
                    {campsite.campsite_id}
                  </a>)
              </Typography>
              <Typography variant="body2" gutterBottom>
                Accessible: {campsite.accessible ? 'Yes' : 'No'}
              </Typography>
              <Typography variant="body2" gutterBottom>
                Attributes:
              </Typography>
              <List dense>
                {campsite.attributes.map(([key, value]) => (
                  <ListItem key={key}>
                    <ListItemText primary={`${key}: ${value}`} />
                  </ListItem>
                ))}
              </List>
              <Typography variant="body2" gutterBottom>
                Availability:
              </Typography>
              <List dense>
                {campsite.available.map(([start, end], index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={`From: ${new Date(start).toLocaleDateString()} To: ${new Date(
                        end
                      ).toLocaleDateString()}`}
                    />
                  </ListItem>
                ))}
              </List>
              <Typography variant="body2" gutterBottom>
                Weather:
              </Typography>
              <List dense>
                {campsite.weathers.map((weather, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={`Min Temp: ${weather.min_temp}°C, Max Temp: ${weather.max_temp}°C, Humidity: ${weather.humidity}%, Rain: ${weather.rain_amount_mm}mm`}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Paper>
  );
}

export default Campground;
