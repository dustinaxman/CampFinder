import React, { useState } from 'react';
import { Accordion, AccordionSummary, AccordionDetails, Typography, Grid, List, ListItem } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const CampgroundList = ({ campgrounds }) => {
  const [expanded, setExpanded] = useState(false);

  const handleAccordionChange = (panel) => (event, isExpanded) => {
    setExpanded(isExpanded ? panel : false);
  };

  // Function to format available dates
  const formatAvailableDates = (datesArray) => {
    if (!datesArray || datesArray.length === 0) return "No availability";
    return datesArray.map(([start, end], index) => (
      <div key={index}>
        From: {new Date(start).toLocaleDateString()} To: {new Date(end).toLocaleDateString()}
      </div>
    ));
  };

  return (
    <div>
      {campgrounds.map((campground, index) => (
        <Accordion 
          expanded={expanded === index} 
          onChange={handleAccordionChange(index)} 
          key={campground.id}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">
              {campground.name} (ID: {campground.id}) {/* Displaying campground ID */}
            </Typography>
            <Typography variant="subtitle1" style={{ marginLeft: 'auto' }}>
              Rating: {campground.rating?.average_rating || 'N/A'} ({campground.rating?.number_of_ratings || '0'} reviews) {/* Displaying average rating */}
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="body1">
                  Activities: {campground.activities.join(', ')}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body1">
                  Amenities: {campground.amenities.join(', ')}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="h6">Campsites:</Typography>
                <List>
                  {campground.campsites.map((campsite) => (
                    <ListItem key={campsite.campsite_id}>
                      <Typography variant="body2">
                        {campsite.name} (ID: {campsite.campsite_id}) - Available: {formatAvailableDates(campsite.available)}
                      </Typography>
                    </ListItem>
                  ))}
                </List>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>
      ))}
    </div>
  );
};

export default CampgroundList;

