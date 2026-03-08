#!/usr/bin/env python3
"""
BioDock AI Copilot - Generalization Bounty Task
Natural Language → Runnable BioDock Script Generator

This AI copilot accepts natural language analysis requests and generates
runnable BioDock-compatible Python scripts for various tissue analysis tasks.

Author: BioDock Hackathon Team
"""

import json
import os
import ast
import re
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging
from datetime import datetime

# AI/ML imports
try:
    import openai
    from langchain.llms import OpenAI
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("Warning: LangChain not available, using simplified text generation")

# Code formatting
try:
    import black
    BLACK_AVAILABLE = True
except ImportError:
    BLACK_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ProjectSchema:
    """
    Represents the schema of a BioDock project with available object classes and features
    """
    tissue_type: str
    object_classes: List[str]
    available_features: List[str]
    file_paths: Dict[str, str]
    coordinate_system: str = "pixel"
    units: str = "pixels"

@dataclass
class WorkflowStep:
    """
    Represents a single step in the analysis workflow
    """
    step_number: int
    operation: str
    description: str
    input_data: str
    output_data: str
    code_snippet: str

@dataclass
class GeneratedScript:
    """
    Represents a complete generated BioDock script with metadata
    """
    script_code: str
    workflow_steps: List[WorkflowStep]
    estimated_outputs: List[str]
    dependencies: List[str]
    execution_notes: str

class BioDockScriptTemplates:
    """
    Library of BioDock script templates and code patterns
    """

    @staticmethod
    def get_base_imports() -> str:
        """Standard imports for BioDock scripts"""
        return '''import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from shapely.geometry import shape, Point, Polygon, MultiPolygon
from shapely.ops import unary_union
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)'''

    @staticmethod
    def get_data_loading_template() -> str:
        """Template for loading various BioDock data formats"""
        return '''
def load_geojson_data(file_path: str) -> Dict:
    """Load GeoJSON segmentation data"""
    with open(file_path, 'r') as f:
        return json.load(f)

def load_csv_metrics(file_path: str) -> pd.DataFrame:
    """Load CSV file with pre-computed metrics"""
    return pd.read_csv(file_path)

def classify_objects_by_type(geojson_data: Dict, target_types: List[str]) -> Dict[str, List]:
    """Classify objects by type from GeoJSON features"""
    classified = {obj_type: [] for obj_type in target_types}

    for feature in geojson_data.get('features', []):
        properties = feature.get('properties', {})
        geometry = feature.get('geometry')

        if not geometry:
            continue

        # Extract object type
        obj_type = extract_object_type(properties, target_types)
        if obj_type:
            geom = shape(geometry)
            classified[obj_type].append({
                'id': properties.get('id', f'unknown_{len(classified[obj_type])}'),
                'geometry': geom,
                'centroid': geom.centroid,
                'area': geom.area,
                'properties': properties
            })

    return classified

def extract_object_type(properties: Dict, target_types: List[str]) -> Optional[str]:
    """Extract object type from properties"""
    type_fields = ['type', 'class', 'classification', 'object_type', 'label']

    for field in type_fields:
        if field in properties:
            value = str(properties[field]).lower()
            for target_type in target_types:
                if target_type.lower() in value:
                    return target_type
    return None'''

    @staticmethod
    def get_distance_analysis_template() -> str:
        """Template for distance-based analyses"""
        return '''
def compute_nearest_distances(source_objects: List, target_objects: List) -> List[Dict]:
    """Compute distances from source objects to nearest target objects"""
    results = []

    for src_obj in source_objects:
        min_distance = float('inf')
        nearest_target = None

        for tgt_obj in target_objects:
            distance = src_obj['centroid'].distance(tgt_obj['geometry'])
            if distance < min_distance:
                min_distance = distance
                nearest_target = tgt_obj

        if nearest_target:
            results.append({
                'source_id': src_obj['id'],
                'target_id': nearest_target['id'],
                'distance': min_distance,
                'source_area': src_obj['area'],
                'target_area': nearest_target['area']
            })

    return results'''

    @staticmethod
    def get_area_analysis_template() -> str:
        """Template for area-based analyses"""
        return '''
def compute_area_ratios(numerator_objects: List, denominator_objects: List) -> Dict:
    """Compute area ratios between object types"""
    numerator_area = sum(obj['area'] for obj in numerator_objects)
    denominator_area = sum(obj['area'] for obj in denominator_objects)

    ratio = numerator_area / denominator_area if denominator_area > 0 else 0

    return {
        'numerator_area': numerator_area,
        'denominator_area': denominator_area,
        'ratio': ratio,
        'percentage': ratio * 100
    }

def compute_total_tissue_area(tissue_mask_file: str) -> float:
    """Compute total tissue area from mask"""
    # Implementation depends on mask format
    # This is a placeholder
    return 1000000.0  # Default large area'''

    @staticmethod
    def get_morphology_analysis_template() -> str:
        """Template for morphological feature analysis"""
        return '''
def compute_circularity(geometry) -> float:
    """Compute circularity score for a geometry"""
    area = geometry.area
    perimeter = geometry.length
    if perimeter == 0:
        return 0
    return 4 * np.pi * area / (perimeter ** 2)

def compute_morphological_features(objects: List) -> List[Dict]:
    """Compute morphological features for objects"""
    features = []

    for obj in objects:
        geom = obj['geometry']
        centroid = obj['centroid']

        feature_dict = {
            'id': obj['id'],
            'area': geom.area,
            'perimeter': geom.length,
            'circularity': compute_circularity(geom),
            'centroid_x': centroid.x,
            'centroid_y': centroid.y,
            'bounding_box_area': (geom.bounds[2] - geom.bounds[0]) * (geom.bounds[3] - geom.bounds[1])
        }

        features.append(feature_dict)

    return features'''

    @staticmethod
    def get_spatial_grid_template() -> str:
        """Template for spatial grid analysis"""
        return '''
def create_spatial_density_grid(objects: List, grid_size: Tuple[int, int],
                               bounds: Tuple[float, float, float, float]) -> np.ndarray:
    """Create spatial density grid for objects"""
    grid = np.zeros(grid_size)
    min_x, min_y, max_x, max_y = bounds

    cell_width = (max_x - min_x) / grid_size[1]
    cell_height = (max_y - min_y) / grid_size[0]

    for obj in objects:
        centroid = obj['centroid']

        # Convert coordinates to grid indices
        col = int((centroid.x - min_x) / cell_width)
        row = int((centroid.y - min_y) / cell_height)

        # Ensure indices are within bounds
        col = max(0, min(col, grid_size[1] - 1))
        row = max(0, min(row, grid_size[0] - 1))

        grid[row, col] += 1

    return grid

def visualize_spatial_grid(grid: np.ndarray, output_file: str = "spatial_heatmap.png"):
    """Visualize spatial density grid as heatmap"""
    plt.figure(figsize=(10, 8))
    sns.heatmap(grid, cmap='viridis', cbar_kws={'label': 'Object Density'})
    plt.title('Spatial Density Heatmap')
    plt.xlabel('X Grid Position')
    plt.ylabel('Y Grid Position')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()'''

    @staticmethod
    def get_visualization_template() -> str:
        """Template for creating visualizations"""
        return '''
def create_analysis_visualization(data: List[Dict], analysis_type: str,
                                output_file: str = "analysis_result.png"):
    """Create visualization for analysis results"""
    if analysis_type == "distance":
        distances = [item['distance'] for item in data]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Histogram
        ax1.hist(distances, bins=20, alpha=0.7, color='steelblue', edgecolor='black')
        ax1.set_xlabel('Distance')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Distance Distribution')
        ax1.grid(True, alpha=0.3)

        # Box plot
        ax2.boxplot(distances)
        ax2.set_ylabel('Distance')
        ax2.set_title('Distance Box Plot')
        ax2.grid(True, alpha=0.3)

    elif analysis_type == "area":
        areas = [item['area'] for item in data]

        plt.figure(figsize=(10, 6))
        plt.hist(areas, bins=20, alpha=0.7, color='green', edgecolor='black')
        plt.xlabel('Area')
        plt.ylabel('Frequency')
        plt.title('Area Distribution')
        plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()'''

class BioDockCopilot:
    """
    AI Copilot for generating BioDock scripts from natural language instructions
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize the BioDock Copilot

        Args:
            api_key: OpenAI API key (if using OpenAI models)
            model: Model name to use for generation
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.templates = BioDockScriptTemplates()

        # Initialize language model if available
        if LANGCHAIN_AVAILABLE and self.api_key:
            try:
                self.llm = OpenAI(openai_api_key=self.api_key, model_name=model)
                logger.info(f"Initialized OpenAI model: {model}")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI model: {e}")
                self.llm = None
        else:
            self.llm = None
            logger.info("Running in template-based mode (no LLM available)")

    def parse_natural_language_request(self, request: str, schema: ProjectSchema) -> Dict[str, Any]:
        """
        Parse natural language request to extract key analysis parameters

        Args:
            request: Natural language analysis request
            schema: Project schema with available object types and features

        Returns:
            Parsed request parameters
        """
        request_lower = request.lower()

        # Extract analysis type
        analysis_type = "custom"
        if "distance" in request_lower:
            analysis_type = "distance"
        elif "area" in request_lower or "ratio" in request_lower:
            analysis_type = "area"
        elif "circularity" in request_lower or "morpholog" in request_lower:
            analysis_type = "morphology"
        elif "grid" in request_lower or "density" in request_lower or "heatmap" in request_lower:
            analysis_type = "spatial_grid"

        # Extract object types mentioned
        mentioned_objects = []
        for obj_type in schema.object_classes:
            if obj_type.lower() in request_lower:
                mentioned_objects.append(obj_type)

        # Extract measurement keywords
        measurements = []
        measurement_keywords = ["distance", "area", "ratio", "circularity", "size", "count", "density"]
        for keyword in measurement_keywords:
            if keyword in request_lower:
                measurements.append(keyword)

        # Extract output format requirements
        output_formats = []
        if "csv" in request_lower or "table" in request_lower:
            output_formats.append("csv")
        if "plot" in request_lower or "visualization" in request_lower or "heatmap" in request_lower:
            output_formats.append("plot")

        # Extract filtering criteria
        filters = []
        filter_patterns = [
            r"below (\d+\.?\d*)",
            r"above (\d+\.?\d*)",
            r"greater than (\d+\.?\d*)",
            r"less than (\d+\.?\d*)"
        ]

        for pattern in filter_patterns:
            matches = re.findall(pattern, request_lower)
            if matches:
                filters.extend(matches)

        return {
            "analysis_type": analysis_type,
            "mentioned_objects": mentioned_objects,
            "measurements": measurements,
            "output_formats": output_formats,
            "filters": filters,
            "original_request": request
        }

    def generate_workflow_plan(self, parsed_request: Dict, schema: ProjectSchema) -> List[WorkflowStep]:
        """
        Generate a step-by-step workflow plan for the analysis

        Args:
            parsed_request: Parsed natural language request
            schema: Project schema

        Returns:
            List of workflow steps
        """
        steps = []
        step_counter = 1

        # Step 1: Data loading
        steps.append(WorkflowStep(
            step_number=step_counter,
            operation="data_loading",
            description="Load segmentation data from GeoJSON file",
            input_data="GeoJSON file with segmented objects",
            output_data="Parsed object geometries and metadata",
            code_snippet="geojson_data = load_geojson_data(input_file)"
        ))
        step_counter += 1

        # Step 2: Object classification
        if parsed_request["mentioned_objects"]:
            steps.append(WorkflowStep(
                step_number=step_counter,
                operation="object_classification",
                description=f"Classify objects into types: {', '.join(parsed_request['mentioned_objects'])}",
                input_data="Raw segmentation features",
                output_data="Classified object lists by type",
                code_snippet=f"classified_objects = classify_objects_by_type(geojson_data, {parsed_request['mentioned_objects']})"
            ))
            step_counter += 1

        # Step 3: Analysis computation
        analysis_type = parsed_request["analysis_type"]

        if analysis_type == "distance":
            steps.append(WorkflowStep(
                step_number=step_counter,
                operation="distance_computation",
                description="Compute distances between object types",
                input_data="Classified object geometries",
                output_data="Distance measurements",
                code_snippet="distance_results = compute_nearest_distances(source_objects, target_objects)"
            ))

        elif analysis_type == "area":
            steps.append(WorkflowStep(
                step_number=step_counter,
                operation="area_computation",
                description="Compute area measurements and ratios",
                input_data="Classified object geometries",
                output_data="Area measurements and ratios",
                code_snippet="area_results = compute_area_ratios(numerator_objects, denominator_objects)"
            ))

        elif analysis_type == "morphology":
            steps.append(WorkflowStep(
                step_number=step_counter,
                operation="morphology_computation",
                description="Compute morphological features (circularity, area, perimeter)",
                input_data="Object geometries",
                output_data="Morphological feature measurements",
                code_snippet="morphology_results = compute_morphological_features(objects)"
            ))

        elif analysis_type == "spatial_grid":
            steps.append(WorkflowStep(
                step_number=step_counter,
                operation="spatial_grid_computation",
                description="Create spatial density grid",
                input_data="Object centroids and tissue boundaries",
                output_data="2D density grid",
                code_snippet="density_grid = create_spatial_density_grid(objects, grid_size, bounds)"
            ))

        step_counter += 1

        # Step 4: Filtering (if specified)
        if parsed_request["filters"]:
            steps.append(WorkflowStep(
                step_number=step_counter,
                operation="filtering",
                description=f"Apply filters: {', '.join(parsed_request['filters'])}",
                input_data="Raw analysis results",
                output_data="Filtered results",
                code_snippet="filtered_results = apply_filters(results, filter_criteria)"
            ))
            step_counter += 1

        # Step 5: Output generation
        if "csv" in parsed_request["output_formats"]:
            steps.append(WorkflowStep(
                step_number=step_counter,
                operation="csv_output",
                description="Save results to CSV file",
                input_data="Analysis results",
                output_data="CSV file with measurements",
                code_snippet="df.to_csv('analysis_results.csv', index=False)"
            ))
            step_counter += 1

        if "plot" in parsed_request["output_formats"]:
            steps.append(WorkflowStep(
                step_number=step_counter,
                operation="visualization",
                description="Create visualization plots",
                input_data="Analysis results",
                output_data="Plot files (PNG/PDF)",
                code_snippet="create_analysis_visualization(results, analysis_type, 'analysis_plot.png')"
            ))

        return steps

    def generate_script_code(self, workflow_steps: List[WorkflowStep],
                           parsed_request: Dict, schema: ProjectSchema) -> str:
        """
        Generate the complete Python script code

        Args:
            workflow_steps: Planned workflow steps
            parsed_request: Parsed request parameters
            schema: Project schema

        Returns:
            Complete Python script as string
        """
        # Start with base imports
        script_lines = [self.templates.get_base_imports()]

        # Add utility functions based on analysis type
        analysis_type = parsed_request["analysis_type"]

        script_lines.append(self.templates.get_data_loading_template())

        if analysis_type == "distance":
            script_lines.append(self.templates.get_distance_analysis_template())
        elif analysis_type == "area":
            script_lines.append(self.templates.get_area_analysis_template())
        elif analysis_type == "morphology":
            script_lines.append(self.templates.get_morphology_analysis_template())
        elif analysis_type == "spatial_grid":
            script_lines.append(self.templates.get_spatial_grid_template())

        # Always add visualization functions
        script_lines.append(self.templates.get_visualization_template())

        # Generate main function
        main_function = self._generate_main_function(workflow_steps, parsed_request, schema)
        script_lines.append(main_function)

        # Add command-line interface
        cli_code = self._generate_cli_interface(parsed_request)
        script_lines.append(cli_code)

        # Join all parts
        complete_script = "\n\n".join(script_lines)

        # Format with black if available
        if BLACK_AVAILABLE:
            try:
                complete_script = black.format_str(complete_script, mode=black.FileMode())
            except Exception as e:
                logger.warning(f"Failed to format code with black: {e}")

        return complete_script

    def _generate_main_function(self, workflow_steps: List[WorkflowStep],
                              parsed_request: Dict, schema: ProjectSchema) -> str:
        """Generate the main analysis function"""

        function_template = '''
def run_analysis(input_file: str, output_csv: str = "analysis_results.csv",
                output_plot: str = "analysis_plot.png"):
    """
    Run {analysis_description} analysis

    Args:
        input_file: Input GeoJSON file with segmentation data
        output_csv: Output CSV file for results
        output_plot: Output plot file for visualization
    """
    logger.info("Starting {analysis_description} analysis")

    try:
        # Load data
        geojson_data = load_geojson_data(input_file)
        logger.info(f"Loaded {{len(geojson_data.get('features', []))}} objects")

{main_analysis_code}

        logger.info("Analysis completed successfully")

    except Exception as e:
        logger.error(f"Analysis failed: {{e}}")
        raise'''

        # Generate main analysis code based on request type
        analysis_type = parsed_request["analysis_type"]
        mentioned_objects = parsed_request["mentioned_objects"]

        if analysis_type == "distance" and len(mentioned_objects) >= 2:
            source_type, target_type = mentioned_objects[0], mentioned_objects[1]
            main_code = f'''
        # Classify objects
        classified_objects = classify_objects_by_type(geojson_data, {mentioned_objects})
        source_objects = classified_objects['{source_type}']
        target_objects = classified_objects['{target_type}']

        logger.info(f"Found {{len(source_objects)}} {source_type} and {{len(target_objects)}} {target_type}")

        # Compute distances
        results = compute_nearest_distances(source_objects, target_objects)

        # Save to CSV
        df = pd.DataFrame(results)
        df.to_csv(output_csv, index=False)
        logger.info(f"Results saved to {{output_csv}}")

        # Create visualization
        create_analysis_visualization(results, "distance", output_plot)
        logger.info(f"Visualization saved to {{output_plot}}")'''

        elif analysis_type == "area" and mentioned_objects:
            main_code = f'''
        # Classify objects
        classified_objects = classify_objects_by_type(geojson_data, {mentioned_objects})

        # Compute area measurements
        area_results = []
        for obj_type, objects in classified_objects.items():
            total_area = sum(obj['area'] for obj in objects)
            area_results.append({{'object_type': obj_type, 'total_area': total_area, 'count': len(objects)}})

        # Save to CSV
        df = pd.DataFrame(area_results)
        df.to_csv(output_csv, index=False)
        logger.info(f"Area results saved to {{output_csv}}")

        # Create visualization
        create_analysis_visualization(area_results, "area", output_plot)'''

        elif analysis_type == "morphology" and mentioned_objects:
            obj_type = mentioned_objects[0]
            main_code = f'''
        # Classify objects
        classified_objects = classify_objects_by_type(geojson_data, ['{obj_type}'])
        objects = classified_objects['{obj_type}']

        # Compute morphological features
        morphology_results = compute_morphological_features(objects)

        # Apply filters if specified
        filtered_results = [r for r in morphology_results if r['circularity'] >= 0.0]  # Modify threshold as needed

        # Save to CSV
        df = pd.DataFrame(filtered_results)
        df.to_csv(output_csv, index=False)
        logger.info(f"Morphology results saved to {{output_csv}}")

        # Create visualization
        create_analysis_visualization(filtered_results, "morphology", output_plot)'''

        elif analysis_type == "spatial_grid":
            main_code = '''
        # Extract all objects for spatial analysis
        all_objects = []
        for feature in geojson_data.get('features', []):
            geom = shape(feature.get('geometry'))
            all_objects.append({'centroid': geom.centroid, 'area': geom.area})

        # Determine spatial bounds
        bounds = (0, 0, 1000, 1000)  # Default bounds, should be computed from actual data

        # Create spatial density grid
        density_grid = create_spatial_density_grid(all_objects, (50, 50), bounds)

        # Save grid data
        np.savetxt(output_csv.replace('.csv', '_grid.csv'), density_grid, delimiter=',')

        # Create heatmap visualization
        visualize_spatial_grid(density_grid, output_plot)
        logger.info(f"Spatial heatmap saved to {output_plot}")'''

        else:
            # Generic analysis
            main_code = '''
        # Generic object analysis
        objects = []
        for feature in geojson_data.get('features', []):
            geom = shape(feature.get('geometry'))
            objects.append({
                'id': feature.get('properties', {}).get('id', 'unknown'),
                'area': geom.area,
                'centroid_x': geom.centroid.x,
                'centroid_y': geom.centroid.y
            })

        # Save results
        df = pd.DataFrame(objects)
        df.to_csv(output_csv, index=False)
        logger.info(f"Object data saved to {output_csv}")'''

        # Format the complete function
        return function_template.format(
            analysis_description=analysis_type.replace("_", " "),
            main_analysis_code=main_code
        )

    def _generate_cli_interface(self, parsed_request: Dict) -> str:
        """Generate command-line interface"""
        return '''
def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(description="BioDock Script Generated by AI Copilot")
    parser.add_argument('--input', '-i', required=True, help='Input GeoJSON file')
    parser.add_argument('--csv-output', '-c', default='analysis_results.csv', help='Output CSV file')
    parser.add_argument('--plot-output', '-p', default='analysis_plot.png', help='Output plot file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        run_analysis(args.input, args.csv_output, args.plot_output)
        print(f"Analysis completed successfully!")
        print(f"Results: {args.csv_output}")
        print(f"Plot: {args.plot_output}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()'''

    def create_workflow_visualization(self, workflow_steps: List[WorkflowStep],
                                    output_file: str = "workflow_diagram.png") -> str:
        """
        Create a visual representation of the planned workflow

        Args:
            workflow_steps: List of workflow steps
            output_file: Output file for the diagram

        Returns:
            Path to the created diagram
        """
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches

        fig, ax = plt.subplots(figsize=(12, 8))

        # Define colors for different operation types
        color_map = {
            'data_loading': '#3498db',
            'object_classification': '#2ecc71',
            'distance_computation': '#e74c3c',
            'area_computation': '#f39c12',
            'morphology_computation': '#9b59b6',
            'spatial_grid_computation': '#1abc9c',
            'filtering': '#34495e',
            'csv_output': '#95a5a6',
            'visualization': '#e67e22'
        }

        box_height = 0.8
        box_width = 2.0
        y_spacing = 1.5

        for i, step in enumerate(workflow_steps):
            y_pos = len(workflow_steps) - i - 1

            # Draw box
            color = color_map.get(step.operation, '#bdc3c7')
            box = patches.Rectangle(
                (0, y_pos * y_spacing), box_width, box_height,
                linewidth=1, edgecolor='black', facecolor=color, alpha=0.7
            )
            ax.add_patch(box)

            # Add step text
            ax.text(box_width/2, y_pos * y_spacing + box_height/2,
                   f"Step {step.step_number}: {step.operation}",
                   ha='center', va='center', fontsize=10, fontweight='bold')

            # Add description
            ax.text(box_width + 0.2, y_pos * y_spacing + box_height/2,
                   step.description,
                   ha='left', va='center', fontsize=9, wrap=True)

            # Draw arrow to next step
            if i < len(workflow_steps) - 1:
                ax.arrow(box_width/2, y_pos * y_spacing - 0.1,
                        0, -y_spacing + box_height + 0.2,
                        head_width=0.1, head_length=0.1,
                        fc='black', ec='black')

        ax.set_xlim(-0.5, 8)
        ax.set_ylim(-0.5, len(workflow_steps) * y_spacing)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('BioDock Analysis Workflow', fontsize=16, fontweight='bold', pad=20)

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Workflow diagram saved to {output_file}")
        return output_file

    def generate_script(self, natural_language_request: str,
                       project_schema: ProjectSchema) -> GeneratedScript:
        """
        Generate a complete BioDock script from natural language request

        Args:
            natural_language_request: Natural language description of analysis
            project_schema: Schema describing available data and object types

        Returns:
            Generated script with metadata
        """
        logger.info(f"Generating script for request: {natural_language_request}")

        # Parse the request
        parsed_request = self.parse_natural_language_request(natural_language_request, project_schema)
        logger.info(f"Parsed request: {parsed_request}")

        # Generate workflow plan
        workflow_steps = self.generate_workflow_plan(parsed_request, project_schema)
        logger.info(f"Generated {len(workflow_steps)} workflow steps")

        # Generate script code
        script_code = self.generate_script_code(workflow_steps, parsed_request, project_schema)

        # Determine dependencies
        dependencies = [
            "pandas", "numpy", "matplotlib", "seaborn", "shapely", "argparse", "logging", "json"
        ]

        # Estimate outputs
        estimated_outputs = []
        if "csv" in parsed_request["output_formats"] or parsed_request["analysis_type"] != "spatial_grid":
            estimated_outputs.append("analysis_results.csv")
        if "plot" in parsed_request["output_formats"] or parsed_request["analysis_type"] == "spatial_grid":
            estimated_outputs.append("analysis_plot.png")

        # Generate execution notes
        execution_notes = f"""
Generated BioDock script for: {natural_language_request}

Analysis Type: {parsed_request['analysis_type']}
Target Objects: {', '.join(parsed_request['mentioned_objects'])}
Measurements: {', '.join(parsed_request['measurements'])}

To run this script:
1. Ensure all dependencies are installed: pip install {' '.join(dependencies)}
2. Place your GeoJSON file in the working directory
3. Run: python script.py --input your_data.geojson

Expected outputs: {', '.join(estimated_outputs)}
"""

        return GeneratedScript(
            script_code=script_code,
            workflow_steps=workflow_steps,
            estimated_outputs=estimated_outputs,
            dependencies=dependencies,
            execution_notes=execution_notes
        )

def main():
    """
    Command-line interface for the BioDock Copilot
    """
    import argparse

    parser = argparse.ArgumentParser(description="BioDock AI Copilot")
    parser.add_argument('--request', '-r', required=True,
                       help='Natural language analysis request')
    parser.add_argument('--tissue-type', '-t', default='kidney',
                       help='Tissue type being analyzed')
    parser.add_argument('--object-classes', '-o',
                       default='glomerulus,vessel,epithelial_cell,immune_cell',
                       help='Comma-separated list of available object classes')
    parser.add_argument('--output-script', '-s', default='generated_script.py',
                       help='Output file for generated script')
    parser.add_argument('--output-workflow', '-w', default='workflow_diagram.png',
                       help='Output file for workflow diagram')

    args = parser.parse_args()

    # Create project schema
    schema = ProjectSchema(
        tissue_type=args.tissue_type,
        object_classes=args.object_classes.split(','),
        available_features=['area', 'perimeter', 'circularity', 'centroid'],
        file_paths={'geojson': 'segmentation.geojson', 'csv': 'metrics.csv'}
    )

    # Initialize copilot
    copilot = BioDockCopilot()

    # Generate script
    try:
        generated_script = copilot.generate_script(args.request, schema)

        # Save generated script
        with open(args.output_script, 'w') as f:
            f.write(generated_script.script_code)

        # Create workflow diagram
        copilot.create_workflow_visualization(
            generated_script.workflow_steps,
            args.output_workflow
        )

        print(f"Generated script saved to: {args.output_script}")
        print(f"Workflow diagram saved to: {args.output_workflow}")
        print("\nExecution Notes:")
        print(generated_script.execution_notes)

    except Exception as e:
        print(f"Error generating script: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()