import React, { useState } from 'react';
import { TextField, Button, Grid, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

const QueryFilterForm = ({ query, setQuery, errors }) => {
  const [currentCondition, setCurrentCondition] = useState({});
  const [currentLogicalGroup, setCurrentLogicalGroup] = useState('AND');

  const handleAddCondition = () => {
    if (!currentCondition || !Object.keys(currentCondition).length) return;

    setQuery((prevQuery) => ({
      ...prevQuery,
      filters: {
        ...prevQuery.filters,
        [currentLogicalGroup]: [...prevQuery.filters[currentLogicalGroup], currentCondition],
      },
    }));

    setCurrentCondition({});
  };

  const handleConditionChange = (field, value) => {
    setCurrentCondition({ [field]: value });
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <FormControl fullWidth>
          <InputLabel>Logical Group</InputLabel>
          <Select
            value={currentLogicalGroup}
            onChange={(e) => setCurrentLogicalGroup(e.target.value)}
          >
            <MenuItem value="AND">AND</MenuItem>
            <MenuItem value="OR">OR</MenuItem>
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          label="Condition Field (e.g., rating.average_rating)"
          fullWidth
          onChange={(e) => handleConditionChange('field', e.target.value)}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          label="Condition Value (e.g., gt: 4.0)"
          fullWidth
          onChange={(e) => handleConditionChange('value', e.target.value)}
        />
      </Grid>

      <Grid item xs={12}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleAddCondition}
        >
          Add Condition
        </Button>
      </Grid>

      {/* Display errors */}
      {errors && (
        <Grid item xs={12}>
          {Object.entries(errors).map(([key, value]) => (
            <p key={key} style={{ color: 'red' }}>
              {key}: {value}
            </p>
          ))}
        </Grid>
      )}
    </Grid>
  );
};

export default QueryFilterForm;
