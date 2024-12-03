import React, { useState } from 'react';
import {
  TextField,
  Button,
  MenuItem,
  Select,
  InputLabel,
  FormControl,
  Checkbox,
  ListItemText,
  Box,
} from '@mui/material';

// Allowed fields and their corresponding value types
const FILTER_OPTIONS = {
  "rating.average_rating": ["gt", "ge", "lt", "le", "eq", "between"],
  "campsites.accessible": ["eq"],
  "amenities": ["contains"],
  "activities": ["contains_any"],
  "campsites.attributes": ["contains"],
};

const AMENITIES_OPTIONS = ["accessible boat dock", "campfire rings", "drinking water", "restrooms"];
const ACTIVITIES_OPTIONS = ["hiking", "fishing", "swimming", "kayaking"];
const ATTRIBUTES_OPTIONS = [
  { label: "campfire allowed", type: "boolean" },
  { label: "driveway length", type: "number" },
];

const QueryFilterForm = ({ onFilterSubmit }) => {
  const [filters, setFilters] = useState([]);
  const [currentFilter, setCurrentFilter] = useState({ field: "", operator: "", value: "" });

  const handleAddFilter = () => {
    setFilters((prevFilters) => [...prevFilters, currentFilter]);
    setCurrentFilter({ field: "", operator: "", value: "" });
  };

  const handleFieldChange = (field) => {
    setCurrentFilter((prev) => ({ ...prev, field, operator: "", value: "" }));
  };

  const handleOperatorChange = (operator) => {
    setCurrentFilter((prev) => ({ ...prev, operator }));
  };

  const handleValueChange = (value) => {
    setCurrentFilter((prev) => ({ ...prev, value }));
  };

  const renderValueInput = () => {
    if (!currentFilter.field || !currentFilter.operator) return null;

    const fieldOptions = currentFilter.field === "amenities" ? AMENITIES_OPTIONS
      : currentFilter.field === "activities" ? ACTIVITIES_OPTIONS
      : ATTRIBUTES_OPTIONS.find((attr) => attr.label === currentFilter.field)?.type === "boolean"
      ? (
          <Checkbox
            checked={currentFilter.value === true}
            onChange={(e) => handleValueChange(e.target.checked)}
          />
        )
      : <TextField onChange={(e) => handleValueChange(e.target.value)} />;

    return (
      <FormControl>
        {currentFilter.field === "amenities" || currentFilter.field === "activities" ? (
          <Select
            multiple
            value={currentFilter.value || []}
            onChange={(e) => handleValueChange(e.target.value)}
            renderValue={(selected) => selected.join(", ")}
          >
            {(currentFilter.field === "amenities" ? AMENITIES_OPTIONS : ACTIVITIES_OPTIONS).map((option) => (
              <MenuItem key={option} value={option}>
                <Checkbox checked={currentFilter.value?.includes(option) || false} />
                <ListItemText primary={option} />
              </MenuItem>
            ))}
          </Select>
        ) : fieldOptions}
      </FormControl>
    );
  };

  return (
    <Box>
      <FormControl>
        <InputLabel>Field</InputLabel>
        <Select value={currentFilter.field} onChange={(e) => handleFieldChange(e.target.value)}>
          {Object.keys(FILTER_OPTIONS).map((field) => (
            <MenuItem key={field} value={field}>
              {field}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      {currentFilter.field && (
        <FormControl>
          <InputLabel>Operator</InputLabel>
          <Select
            value={currentFilter.operator}
            onChange={(e) => handleOperatorChange(e.target.value)}
          >
            {FILTER_OPTIONS[currentFilter.field].map((op) => (
              <MenuItem key={op} value={op}>
                {op}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}
      {renderValueInput()}
      <Button onClick={handleAddFilter}>Add Filter</Button>
      <Button onClick={() => onFilterSubmit(filters)}>Submit Query</Button>
    </Box>
  );
};

export default QueryFilterForm;
