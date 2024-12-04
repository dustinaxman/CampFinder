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
  Typography,
} from '@mui/material';

const FILTER_OPTIONS = {
  "rating.average_rating": ["gt", "ge", "lt", "le", "eq", "between"],
  "rating.number_of_ratings": ["gt", "ge", "lt", "le", "eq", "between"],
  "campsites.accessible": ["eq"],
  "amenities": ["contains", "contains_any"],
  "activities": ["contains", "contains_any"],
  "campsites.attributes": ["contains"],
};

const AMENITIES_OPTIONS = ["accessible boat dock", "campfire rings", "drinking water", "restrooms"];
const ACTIVITIES_OPTIONS = ["hiking", "fishing", "swimming", "kayaking"];
const ATTRIBUTES_OPTIONS = [
  { label: 'campfire allowed', type: 'boolean' },
  { label: 'driveway length', type: 'number' },
];

const WEATHER_FIELDS = ["min_temp", "max_temp", "rain_amount_mm", "humidity"];
const WEATHER_OPERATORS = ["gt", "ge", "lt", "le", "eq", "between"];

const QueryFilterForm = ({ filterType, isWeatherFilter, onFilterUpdate }) => {
  const [filters, setFilters] = useState([]);
  const [currentFilter, setCurrentFilter] = useState({
    field: "",
    operator: "",
    value: "",
    nestedOperator: "",
    nestedValue: "",
  });

  const handleAddFilter = () => {
    if (!currentFilter.field || !currentFilter.operator || currentFilter.value === "") {
      alert("Please complete all filter fields before adding.");
      return;
    }

    const filter = { field: currentFilter.field, operator: currentFilter.operator };

    if (currentFilter.field === "campsites.attributes" && currentFilter.operator === "contains") {
      filter.value = currentFilter.nestedOperator
        ? { [currentFilter.value]: { [currentFilter.nestedOperator]: currentFilter.nestedValue } }
        : currentFilter.value;
    } else {
      filter.value = currentFilter.value;
    }

    const updatedFilters = [...filters, { [filter.field]: { [filter.operator]: filter.value } }];
    setFilters(updatedFilters);
    onFilterUpdate(updatedFilters); // Immediately propagate to parent
    setCurrentFilter({ field: "", operator: "", value: "", nestedOperator: "", nestedValue: "" });
  };

  const handleFieldChange = (field) => {
    setCurrentFilter({ field, operator: "", value: "", nestedOperator: "", nestedValue: "" });
  };

  const handleOperatorChange = (operator) => {
    setCurrentFilter((prev) => ({ ...prev, operator }));
  };

  const handleValueChange = (value) => {
    setCurrentFilter((prev) => ({ ...prev, value }));
  };

  const handleNestedOperatorChange = (nestedOperator) => {
    setCurrentFilter((prev) => ({ ...prev, nestedOperator }));
  };

  const handleNestedValueChange = (nestedValue) => {
    setCurrentFilter((prev) => ({ ...prev, nestedValue }));
  };

  const renderValueInput = () => {
    if (!currentFilter.field || !currentFilter.operator) return null;

    if (isWeatherFilter) {
      return (
        <TextField
          type="number"
          onChange={(e) => handleValueChange(Number(e.target.value))}
          value={currentFilter.value || ""}
        />
      );
    }

    if (currentFilter.field === "amenities" || currentFilter.field === "activities") {
      const options = currentFilter.field === "amenities" ? AMENITIES_OPTIONS : ACTIVITIES_OPTIONS;
      return (
        <Select
          multiple
          value={currentFilter.value || []}
          onChange={(e) => handleValueChange(e.target.value)}
          renderValue={(selected) => selected.join(", ")}
        >
          {options.map((option) => (
            <MenuItem key={option} value={option}>
              <Checkbox checked={currentFilter.value?.includes(option) || false} />
              <ListItemText primary={option} />
            </MenuItem>
          ))}
        </Select>
      );
    }

    if (currentFilter.field === "campsites.attributes" && currentFilter.operator === "contains") {
      return (
        <Box>
          <FormControl style={{ marginRight: '8px' }}>
            <InputLabel>Attribute</InputLabel>
            <Select
              value={currentFilter.value || ""}
              onChange={(e) => handleValueChange(e.target.value)}
            >
              {ATTRIBUTES_OPTIONS.map((attr) => (
                <MenuItem key={attr.label} value={attr.label}>
                  {attr.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          {currentFilter.value &&
            ATTRIBUTES_OPTIONS.find((attr) => attr.label === currentFilter.value)?.type && (
              <FormControl style={{ marginRight: '8px' }}>
                <InputLabel>Nested Operator</InputLabel>
                <Select
                  value={currentFilter.nestedOperator || ""}
                  onChange={(e) => handleNestedOperatorChange(e.target.value)}
                >
                  {WEATHER_OPERATORS.map((op) => (
                    <MenuItem key={op} value={op}>
                      {op}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
          {currentFilter.nestedOperator && (
            <TextField
              type={
                ATTRIBUTES_OPTIONS.find((attr) => attr.label === currentFilter.value)?.type ===
                "number"
                  ? "number"
                  : "text"
              }
              value={currentFilter.nestedValue || ""}
              onChange={(e) => handleNestedValueChange(e.target.value)}
              placeholder="Value"
            />
          )}
        </Box>
      );
    }

    return <TextField onChange={(e) => handleValueChange(e.target.value)} />;
  };

  return (
    <Box>
      <FormControl style={{ marginRight: '8px' }}>
        <InputLabel>{isWeatherFilter ? "Weather Field" : "Field"}</InputLabel>
        <Select
          value={currentFilter.field}
          onChange={(e) => handleFieldChange(e.target.value)}
        >
          {(isWeatherFilter ? WEATHER_FIELDS : Object.keys(FILTER_OPTIONS)).map((field) => (
            <MenuItem key={field} value={field}>
              {field}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      {currentFilter.field && (
        <FormControl style={{ marginRight: '8px' }}>
          <InputLabel>Operator</InputLabel>
          <Select
            value={currentFilter.operator}
            onChange={(e) => handleOperatorChange(e.target.value)}
          >
            {(isWeatherFilter
              ? WEATHER_OPERATORS
              : FILTER_OPTIONS[currentFilter.field] || []
            ).map((op) => (
              <MenuItem key={op} value={op}>
                {op}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}
      {renderValueInput()}
      <Button onClick={handleAddFilter} style={{ marginLeft: '8px' }}>
        Add Filter
      </Button>
      <Box>
        <Typography variant="h6">Current Filters:</Typography>
        {filters.map((filter, index) => (
          <Typography key={index}>{JSON.stringify(filter)}</Typography>
        ))}
      </Box>
    </Box>
  );
};

export default QueryFilterForm;
