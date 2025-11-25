#!/bin/bash

echo "Running pytest tests ..."
coverage run --source src -m pytest

pytest_result=$?
if [ $pytest_result -eq 0 ]; then
    echo "Tests passed successfully."
else
    echo "Tests failed with error code: $pytest_result"
    exit $pytest_result
fi

coverage html
echo "Coverage report generated successfully."
