#!/bin/bash

cd conda-recipe
sh build_recipe.sh --python=3.7
sh build_recipe.sh --python=3.8
sh build_recipe.sh --python=3.9

