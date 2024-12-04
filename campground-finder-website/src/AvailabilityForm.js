import React from 'react';
import {
  TextField,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Checkbox,
  ListItemText,
} from '@mui/material';

const DAYS_OF_WEEK = [
  { label: 'Sunday', value: 6 },
  { label: 'Monday', value: 0 },
  { label: 'Tuesday', value: 1 },
  { label: 'Wednesday', value: 2 },
  { label: 'Thursday', value: 3 },
  { label: 'Friday', value: 4 },
  { label: 'Saturday', value: 5 },
];

const AvailabilityForm = ({ availability, onAvailabilityUpdate }) => {
  const handleChange = (field, value) => {
    onAvailabilityUpdate({
      ...availability,
      [field]: value,
    });
  };

  const handleDaysOfWeekChange = (event) => {
    const {
      target: { value },
    } = event;
    onAvailabilityUpdate({
      ...availability,
      days_of_the_week: typeof value === 'string' ? value.split(',') : value,
    });
  };

  return (
    <Box mt={2}>
      <Grid container spacing={2}>
        {/* Start Window Date */}
        <Grid item xs={12} sm={4}>
          <TextField
            fullWidth
            label="Start Window Date"
            type="date"
            value={availability.start_window_date}
            onChange={(e) => handleChange('start_window_date', e.target.value)}
            InputLabelProps={{ shrink: true }}
          />
        </Grid>

        {/* End Window Date */}
        <Grid item xs={12} sm={4}>
          <TextField
            fullWidth
            label="End Window Date"
            type="date"
            value={availability.end_window_date}
            onChange={(e) => handleChange('end_window_date', e.target.value)}
            InputLabelProps={{ shrink: true }}
          />
        </Grid>

        {/* Number of Nights */}
        <Grid item xs={12} sm={4}>
          <TextField
            fullWidth
            label="Number of Nights"
            type="number"
            value={availability.num_nights}
            onChange={(e) => handleChange('num_nights', parseInt(e.target.value, 10) || 0)}
          />
        </Grid>

        {/* Days of the Week */}
        <Grid item xs={12}>
          <FormControl fullWidth>
            <InputLabel>Days of the Week</InputLabel>
            <Select
              multiple
              value={availability.days_of_the_week}
              onChange={handleDaysOfWeekChange}
              renderValue={(selected) =>
                selected
                  .map((value) => DAYS_OF_WEEK.find((day) => day.value === value)?.label)
                  .join(', ')
              }
            >
              {DAYS_OF_WEEK.map((day) => (
                <MenuItem key={day.value} value={day.value}>
                  <Checkbox checked={availability.days_of_the_week.includes(day.value)} />
                  <ListItemText primary={day.label} />
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AvailabilityForm;
