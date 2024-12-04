import React, { useState } from "react";
import {
  TextField,
  Button,
  MenuItem,
  Select,
  InputLabel,
  FormControl,
  Box,
  Typography,
  IconButton,
  Checkbox,
  ListItemText,
} from "@mui/material";
import { Delete as DeleteIcon } from "@mui/icons-material";

const FILTER_OPTIONS = {
  "rating.average_rating": ["gt", "ge", "lt", "le", "eq", "between"],
  "rating.number_of_ratings": ["gt", "ge", "lt", "le", "eq", "between"],
  "campsites.accessible": ["eq"],
  "amenities": ["contains", "contains_any"],
  "activities": ["contains", "contains_any"],
  "campsites.attributes": ["contains"],
};

const AMENITIES_OPTIONS = [
  "accessible boat dock",
  "campfire rings",
  "drinking water",
  "restrooms",
];
const ACTIVITIES_OPTIONS = ["hiking", "fishing", "swimming", "kayaking"];
const ATTRIBUTES_OPTIONS = [
  { label: "campfire allowed", type: "boolean" },
  { label: "driveway length", type: "number" },
];

const WEATHER_FIELDS = ["min_temp", "max_temp", "rain_amount_mm", "humidity"];
const WEATHER_OPERATORS = ["gt", "ge", "lt", "le", "eq", "between"];

const QueryFilterForm = ({ filterType, isWeatherFilter, onFilterUpdate }) => {
  const [filters, setFilters] = useState(isWeatherFilter ? {} : []);
  const [currentFilter, setCurrentFilter] = useState({
    field: "",
    operator: "",
    value: [],
    nestedOperator: "",
    nestedValue: "",
  });

  const handleAddFilter = () => {
    if (!currentFilter.field || !currentFilter.operator || currentFilter.value === "") {
      alert("Please complete all filter fields before adding.");
      return;
    }

    if (currentFilter.operator === "between") {
      const splitValue =
        typeof currentFilter.value === "string"
          ? currentFilter.value.split(",").map((v) => parseFloat(v.trim()))
          : currentFilter.value;

      if (splitValue.length !== 2 || splitValue.some((v) => isNaN(v))) {
        alert("Please enter two valid values for 'between' separated by a comma.");
        return;
      }
      currentFilter.value = splitValue;
    }

    if (isWeatherFilter) {
      const updatedFilters = {
        ...filters,
        [currentFilter.field]: { [currentFilter.operator]: currentFilter.value },
      };
      setFilters(updatedFilters);
      onFilterUpdate(updatedFilters);
    } else {
      const filter = { field: currentFilter.field, operator: currentFilter.operator };

      if (
        currentFilter.field === "campsites.attributes" &&
        currentFilter.operator === "contains"
      ) {
        filter.value = currentFilter.nestedOperator
          ? { [currentFilter.value]: { [currentFilter.nestedOperator]: currentFilter.nestedValue } }
          : currentFilter.value;
      } else {
        filter.value = currentFilter.value;
      }

      const updatedFilters = [...filters, { [filter.field]: { [filter.operator]: filter.value } }];
      setFilters(updatedFilters);
      onFilterUpdate(updatedFilters);
    }

    setCurrentFilter({ field: "", operator: "", value: [], nestedOperator: "", nestedValue: "" });
  };

  const handleRemoveFilter = (indexOrKey) => {
    if (isWeatherFilter) {
      const updatedFilters = { ...filters };
      delete updatedFilters[indexOrKey];
      setFilters(updatedFilters);
      onFilterUpdate(updatedFilters);
    } else {
      const updatedFilters = filters.filter((_, index) => index !== indexOrKey);
      setFilters(updatedFilters);
      onFilterUpdate(updatedFilters);
    }
  };

  const handleFieldChange = (field) => {
    setCurrentFilter({ field, operator: "", value: [], nestedOperator: "", nestedValue: "" });
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

  const renderNestedValueInput = () => {
    if (!currentFilter.value || !currentFilter.nestedOperator) return null;

    const attributeType = ATTRIBUTES_OPTIONS.find(
      (attr) => attr.label === currentFilter.value
    )?.type;

    if (attributeType === "boolean") {
      return (
        <Select
          value={currentFilter.nestedValue || ""}
          onChange={(e) => handleNestedValueChange(e.target.value)}
        >
          <MenuItem value={true}>True</MenuItem>
          <MenuItem value={false}>False</MenuItem>
        </Select>
      );
    }

    return (
      <TextField
        type="number"
        value={currentFilter.nestedValue || ""}
        onChange={(e) => handleNestedValueChange(parseFloat(e.target.value))}
      />
    );
  };

  const renderValueInput = () => {
    if (!currentFilter.field || !currentFilter.operator) return null;

    if (currentFilter.field === "campsites.attributes" && currentFilter.operator === "contains") {
      return (
        <Box>
          <Select
            value={currentFilter.value || ""}
            onChange={(e) => handleValueChange(e.target.value)}
          >
            {ATTRIBUTES_OPTIONS.map((option) => (
              <MenuItem key={option.label} value={option.label}>
                {option.label}
              </MenuItem>
            ))}
          </Select>
          {currentFilter.value && (
            <Select
              value={currentFilter.nestedOperator || ""}
              onChange={(e) => handleNestedOperatorChange(e.target.value)}
            >
              {["gt", "ge", "lt", "le", "eq", "between"].map((op) => (
                <MenuItem key={op} value={op}>
                  {op}
                </MenuItem>
              ))}
            </Select>
          )}
          {renderNestedValueInput()}
        </Box>
      );
    }

    if (currentFilter.operator === "between") {
      return (
        <Box>
          <TextField
            type="number"
            placeholder="Start"
            value={currentFilter.value?.[0] || ""}
            onChange={(e) =>
              handleValueChange([parseFloat(e.target.value), currentFilter.value?.[1] || ""])
            }
            style={{ marginRight: "8px" }}
          />
          <TextField
            type="number"
            placeholder="End"
            value={currentFilter.value?.[1] || ""}
            onChange={(e) =>
              handleValueChange([currentFilter.value?.[0] || "", parseFloat(e.target.value)])
            }
          />
        </Box>
      );
    }

    if (
      currentFilter.field === "amenities" ||
      currentFilter.field === "activities"
    ) {
      const options =
        currentFilter.field === "amenities"
          ? AMENITIES_OPTIONS
          : ACTIVITIES_OPTIONS;

      return (
        <Select
          multiple
          value={currentFilter.value || []}
          onChange={(e) => handleValueChange(e.target.value)}
          renderValue={(selected) => (Array.isArray(selected) ? selected.join(", ") : "")}
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

    return <TextField onChange={(e) => handleValueChange(e.target.value)} />;
  };

  return (
    <Box>
      <FormControl style={{ marginRight: "8px" }}>
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
        <FormControl style={{ marginRight: "8px" }}>
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
      <Button onClick={handleAddFilter} style={{ marginLeft: "8px" }}>
        Add Filter
      </Button>
      <Box>
        <Typography variant="h6">Current Filters:</Typography>
        {isWeatherFilter
          ? Object.entries(filters).map(([key, value], index) => (
              <Box key={index} display="flex" alignItems="center">
                <Typography>
                  {key}: {JSON.stringify(value)}
                </Typography>
                <IconButton
                  onClick={() => handleRemoveFilter(key)}
                  style={{ color: "red" }}
                >
                  <DeleteIcon />
                </IconButton>
              </Box>
            ))
          : filters.map((filter, index) => (
              <Box key={index} display="flex" alignItems="center">
                <Typography>{JSON.stringify(filter)}</Typography>
                <IconButton
                  onClick={() => handleRemoveFilter(index)}
                  style={{ color: "red" }}
                >
                  <DeleteIcon />
                </IconButton>
              </Box>
            ))}
      </Box>
    </Box>
  );
};

export default QueryFilterForm;
