import React, { useState } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  Tab,
  Tabs,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box p={3}>
          <Typography>{children}</Typography>
        </Box>
      )}
    </div>
  );
}

function CampgroundDetails({ campsites }) {
  const [tabValue, setTabValue] = React.useState(0);

  const handleChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <Box>
      <Tabs value={tabValue} onChange={handleChange}>
        {campsites.map((campsite, index) => (
          <Tab key={campsite.campsite_id} label={campsite.name || `Campsite ${index + 1}`} />
        ))}
      </Tabs>
      {campsites.map((campsite, index) => (
        <TabPanel key={campsite.campsite_id} value={tabValue} index={index}>
          <Typography variant="h6">{campsite.name}</Typography>
          <Typography>Attributes:</Typography>
          <Box>
            {campsite.attributes.map(([attr, value]) => (
              <Typography key={attr}>
                {attr}: {String(value)}
              </Typography>
            ))}
          </Box>
          <Typography>Available Dates:</Typography>
          {campsite.available.map((date, i) => (
            <Typography key={i}>{date}</Typography>
          ))}
        </TabPanel>
      ))}
    </Box>
  );
}

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
            <CampgroundDetails campsites={selectedCampground.campsites} />
          </DialogContent>
        </Dialog>
      )}
    </>
  );
};

export default CampgroundList;
