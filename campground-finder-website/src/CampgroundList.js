import React, { useState } from 'react';
import { Dialog, DialogTitle, DialogContent, Tab, Tabs, Typography, Accordion, AccordionSummary, AccordionDetails } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const CampgroundList = ({ campgrounds }) => {
  const [selectedCampground, setSelectedCampground] = useState(null);

  const handleCampgroundClick = (campground) => {
    setSelectedCampground(campground);
  };

  const handleClose = () => {
    setSelectedCampground(null);
  };

  return (
    <>
      {campgrounds.map((campground) => (
        <Accordion key={campground.id}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">{campground.name}</Typography>
            <Typography variant="subtitle1" style={{ marginLeft: 'auto' }}>
              Rating: {campground.rating?.average_rating || 'N/A'} (
              {campground.rating?.number_of_ratings || '0'} reviews)
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body1">{campground.info}</Typography>
            <Button variant="outlined" onClick={() => handleCampgroundClick(campground)}>
              View Campsites
            </Button>
          </AccordionDetails>
        </Accordion>
      ))}

      {selectedCampground && (
        <Dialog open onClose={handleClose} fullWidth maxWidth="md">
          <DialogTitle>{selectedCampground.name}</DialogTitle>
          <DialogContent>
            <Tabs>
              {selectedCampground.campsites.map((campsite) => (
                <Tab key={campsite.campsite_id} label={campsite.name}>
                  <Typography variant="body1">
                    Attributes: {JSON.stringify(campsite.attributes)}
                  </Typography>
                </Tab>
              ))}
            </Tabs>
          </DialogContent>
        </Dialog>
      )}
    </>
  );
};

export default CampgroundList;
