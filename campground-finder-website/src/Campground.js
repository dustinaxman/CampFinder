import React from 'react';
import { List, ListItem, ListItemText, Typography } from '@mui/material';

function Campground({ campground }) {
  return (
    <div>
      <Typography variant="subtitle1">Activities: {campground.activities.join(', ')}</Typography>
      <Typography variant="subtitle1">Amenities: {campground.amenities.join(', ')}</Typography>

      <List>
        {campground.campsites.map((campsite) => (
          <ListItem key={campsite.campsite_id}>
            <ListItemText
              primary={`${campsite.name} - Available: ${campsite.available.booking_date}`}
              secondary={`Details: ${campsite.attributes.map(([key, value]) => `${key}: ${value}`).join(', ')}`}
            />
          </ListItem>
        ))}
      </List>
    </div>
  );
}

export default Campground;

