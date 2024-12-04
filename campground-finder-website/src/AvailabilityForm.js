import React from 'react';
import { TextField, Box, Typography, Select, MenuItem, FormControl, InputLabel } from '@mui/material';

const AvailabilityForm = ({ availability, onAvailabilityUpdate }) => {
  const handleChange = (field, value) => {
    onAvailabilityUpdate({
      ...availability,
      [field]: value,
    });
  };

  return (
    <Box>
      <TextField
        label="Start Window Date"
        type="date"
        value={availability.start_window_date}
        onChange={(e) => handleChange('start_window_date', e.target.value)}
        InputLabelProps={{ shrink: true }}
        style={{ marginRight: '16px' }}
      />
      <TextField
        label="End Window Date"
        type="date"
        value={availability.end_window_date}
        onChange={(e) => handleChange('end_window_date', e.target.value)}
        InputLabelProps={{ shrink: true }}
      />
      <TextField
        label="Number of Nights"
        type="number"
        value={availability.num_nights}
        onChange={(e) => handleChange('num_nights', parseInt(e.target.value, 10) || 0)}
        style={{ marginTop: '16px', marginRight: '16px' }}
      />
      <FormControl style={{ marginTop: '16px', minWidth: 200 }}>
        <InputLabel>Days of the Week</InputLabel>
        <Select
          multiple
          value={availability.days_of_the_week}
          onChange={(e) => handleChange('days_of_the_week', e.target.value)}
        >
          {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].map(
            (day, index) => (
              <MenuItem key={index} value={index}>
                {day}
              </MenuItem>
            )
          )}
        </Select>
      </FormControl>
    </Box>
  );
};

export default AvailabilityForm;
