#!/usr/bin/env python3
"""
BioDock Hackathon - Baseline Task
Glomerulus-to-Vessel Distance Analysis for Kidney Tissue Segmentation

This script computes the distance from each glomerulus to its nearest vessel
in kidney tissue segmentation data and produces structured outputs.

Author: BioDock Hackathon Team
"""

import json
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
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KidneyTissueAnalyzer:
    """
    Analyzer for kidney tissue segmentation data focusing on glomerulus-vessel spatial relationships
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the analyzer with data directory path

        Args:
            data_dir: Path to directory containing GeoJSON segmentation files
        """
        self.data_dir = Path(data_dir)
        self.glomeruli = []
        self.vessels = []
        self.tissue_mask = None
        self.results = []

        # Object type mappings (may need adjustment based on actual BioDock data format)
        self.object_type_mapping = {
            'glomerulus': ['glomerulus', 'glomeruli', 'Glomerulus', 'GLOMERULUS'],
            'vessel': ['vessel', 'vessels', 'blood_vessel', 'Blood_Vessel', 'VESSEL', 'artery', 'vein']
        }

        logger.info(f"Initialized KidneyTissueAnalyzer with data directory: {self.data_dir}")

    def load_segmentation_data(self, geojson_file: str) -> Dict:
        """
        Load segmentation data from GeoJSON file

        Args:
            geojson_file: Path to GeoJSON file containing segmented objects

        Returns:
            Parsed GeoJSON data dictionary
        """
        geojson_path = self.data_dir / geojson_file

        try:
            with open(geojson_path, 'r') as f:
                data = json.load(f)

            logger.info(f"Loaded GeoJSON data from {geojson_path}")
            logger.info(f"Found {len(data.get('features', []))} segmented objects")

            return data

        except FileNotFoundError:
            logger.error(f"GeoJSON file not found: {geojson_path}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON format in file: {geojson_path}")
            raise

    def classify_objects(self, geojson_data: Dict) -> None:
        """
        Classify segmented objects into glomeruli and vessels based on object properties

        Args:
            geojson_data: Parsed GeoJSON data containing segmented objects
        """
        self.glomeruli.clear()
        self.vessels.clear()

        features = geojson_data.get('features', [])

        for feature in features:
            properties = feature.get('properties', {})
            geometry = feature.get('geometry')

            if not geometry:
                continue

            # Extract object type/class from properties
            # This may vary depending on BioDock's exact format
            object_type = self._extract_object_type(properties)
            object_id = properties.get('id', properties.get('object_id', f"unknown_{len(self.glomeruli + self.vessels)}"))

            # Create shapely geometry object
            try:
                geom = shape(geometry)
                if not geom.is_valid:
                    logger.warning(f"Invalid geometry for object {object_id}, attempting to fix")
                    geom = geom.buffer(0)  # Often fixes invalid geometries

                object_data = {
                    'id': object_id,
                    'geometry': geom,
                    'centroid': geom.centroid,
                    'area': geom.area,
                    'properties': properties
                }

                if object_type == 'glomerulus':
                    self.glomeruli.append(object_data)
                elif object_type == 'vessel':
                    self.vessels.append(object_data)

            except Exception as e:
                logger.warning(f"Failed to process geometry for object {object_id}: {e}")
                continue

        logger.info(f"Classified {len(self.glomeruli)} glomeruli and {len(self.vessels)} vessels")

    def _extract_object_type(self, properties: Dict) -> Optional[str]:
        """
        Extract object type from properties dictionary

        Args:
            properties: Object properties from GeoJSON feature

        Returns:
            Classified object type ('glomerulus', 'vessel', or None)
        """
        # Try common property names for object classification
        type_fields = ['type', 'class', 'classification', 'object_type', 'label', 'category']

        for field in type_fields:
            if field in properties:
                value = str(properties[field]).lower()

                # Check if value matches glomerulus patterns
                for pattern in self.object_type_mapping['glomerulus']:
                    if pattern.lower() in value:
                        return 'glomerulus'

                # Check if value matches vessel patterns
                for pattern in self.object_type_mapping['vessel']:
                    if pattern.lower() in value:
                        return 'vessel'

        return None

    def compute_glomerulus_vessel_distances(self) -> List[Dict]:
        """
        Compute the distance from each glomerulus to its nearest vessel

        Returns:
            List of distance measurements with glomerulus and vessel information
        """
        if not self.glomeruli:
            logger.error("No glomeruli found in the data")
            return []

        if not self.vessels:
            logger.error("No vessels found in the data")
            return []

        results = []

        logger.info("Computing glomerulus-to-vessel distances...")

        for glom in self.glomeruli:
            min_distance = float('inf')
            nearest_vessel = None

            glom_centroid = glom['centroid']

            # Find nearest vessel
            for vessel in self.vessels:
                # Compute distance from glomerulus centroid to vessel edge
                distance = glom_centroid.distance(vessel['geometry'])

                if distance < min_distance:
                    min_distance = distance
                    nearest_vessel = vessel

            if nearest_vessel is not None:
                result = {
                    'glomerulus_id': glom['id'],
                    'nearest_vessel_id': nearest_vessel['id'],
                    'distance': min_distance,
                    'glomerulus_area': glom['area'],
                    'vessel_area': nearest_vessel['area'],
                    'glomerulus_centroid_x': glom_centroid.x,
                    'glomerulus_centroid_y': glom_centroid.y
                }
                results.append(result)

                logger.debug(f"Glomerulus {glom['id']} -> Vessel {nearest_vessel['id']}: {min_distance:.2f} units")
            else:
                logger.warning(f"No nearest vessel found for glomerulus {glom['id']}")

        logger.info(f"Computed distances for {len(results)} glomeruli")
        return results

    def save_results_csv(self, results: List[Dict], output_file: str = "glomeruli_distances.csv") -> None:
        """
        Save distance computation results to CSV file

        Args:
            results: List of distance measurement dictionaries
            output_file: Output CSV filename
        """
        if not results:
            logger.error("No results to save")
            return

        df = pd.DataFrame(results)

        # Ensure required columns are present
        required_columns = ['glomerulus_id', 'nearest_vessel_id', 'distance']
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"Required column '{col}' missing from results")
                return

        # Sort by distance for easier interpretation
        df = df.sort_values('distance')

        # Save to CSV
        df.to_csv(output_file, index=False)
        logger.info(f"Results saved to {output_file}")

        # Log summary statistics
        logger.info(f"Distance summary - Mean: {df['distance'].mean():.3f}, "
                   f"Median: {df['distance'].median():.3f}, "
                   f"Min: {df['distance'].min():.3f}, "
                   f"Max: {df['distance'].max():.3f}")

    def create_distance_visualization(self, results: List[Dict],
                                    output_file: str = "distance_distribution.png") -> None:
        """
        Create visualization of distance distribution

        Args:
            results: List of distance measurement dictionaries
            output_file: Output plot filename
        """
        if not results:
            logger.error("No results to visualize")
            return

        distances = [r['distance'] for r in results]

        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Glomerulus-to-Vessel Distance Analysis', fontsize=16, fontweight='bold')

        # 1. Distance distribution histogram
        ax1.hist(distances, bins=20, alpha=0.7, color='steelblue', edgecolor='black')
        ax1.set_xlabel('Distance (units)')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Distribution of Glomerulus-Vessel Distances')
        ax1.grid(True, alpha=0.3)

        # Add statistics text
        mean_dist = np.mean(distances)
        median_dist = np.median(distances)
        ax1.axvline(mean_dist, color='red', linestyle='--', label=f'Mean: {mean_dist:.2f}')
        ax1.axvline(median_dist, color='orange', linestyle='--', label=f'Median: {median_dist:.2f}')
        ax1.legend()

        # 2. Box plot
        ax2.boxplot(distances, vert=True)
        ax2.set_ylabel('Distance (units)')
        ax2.set_title('Distance Distribution Box Plot')
        ax2.grid(True, alpha=0.3)

        # 3. Cumulative distribution
        sorted_distances = np.sort(distances)
        cumulative = np.arange(1, len(distances) + 1) / len(distances)
        ax3.plot(sorted_distances, cumulative, 'b-', linewidth=2)
        ax3.set_xlabel('Distance (units)')
        ax3.set_ylabel('Cumulative Probability')
        ax3.set_title('Cumulative Distance Distribution')
        ax3.grid(True, alpha=0.3)

        # 4. Summary statistics table
        ax4.axis('off')
        stats_data = {
            'Statistic': ['Count', 'Mean', 'Median', 'Std Dev', 'Min', 'Max', '25th %ile', '75th %ile'],
            'Value': [
                len(distances),
                f"{np.mean(distances):.3f}",
                f"{np.median(distances):.3f}",
                f"{np.std(distances):.3f}",
                f"{np.min(distances):.3f}",
                f"{np.max(distances):.3f}",
                f"{np.percentile(distances, 25):.3f}",
                f"{np.percentile(distances, 75):.3f}"
            ]
        }

        table = ax4.table(cellText=[[stats_data['Statistic'][i], stats_data['Value'][i]]
                                   for i in range(len(stats_data['Statistic']))],
                         colLabels=['Statistic', 'Value'],
                         cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        ax4.set_title('Summary Statistics')

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Visualization saved to {output_file}")

    def run_analysis(self, geojson_file: str,
                    csv_output: str = "glomeruli_distances.csv",
                    plot_output: str = "distance_distribution.png") -> List[Dict]:
        """
        Run complete analysis pipeline

        Args:
            geojson_file: Input GeoJSON file with segmentation data
            csv_output: Output CSV filename
            plot_output: Output plot filename

        Returns:
            Analysis results
        """
        logger.info("Starting glomerulus-vessel distance analysis pipeline")

        try:
            # Load and classify data
            geojson_data = self.load_segmentation_data(geojson_file)
            self.classify_objects(geojson_data)

            # Compute distances
            results = self.compute_glomerulus_vessel_distances()

            if results:
                # Save outputs
                self.save_results_csv(results, csv_output)
                self.create_distance_visualization(results, plot_output)

                logger.info("Analysis completed successfully")
                return results
            else:
                logger.error("No valid results generated")
                return []

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise

def main():
    """
    Command-line interface for the glomerulus-vessel analysis script
    """
    parser = argparse.ArgumentParser(description="Compute glomerulus-to-vessel distances from kidney tissue segmentation")
    parser.add_argument('--input', '-i', default='segmentation.geojson',
                       help='Input GeoJSON file with segmentation data')
    parser.add_argument('--data-dir', '-d', default='data',
                       help='Data directory path')
    parser.add_argument('--csv-output', '-c', default='glomeruli_distances.csv',
                       help='Output CSV filename')
    parser.add_argument('--plot-output', '-p', default='distance_distribution.png',
                       help='Output plot filename')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize analyzer and run analysis
    try:
        analyzer = KidneyTissueAnalyzer(data_dir=args.data_dir)
        results = analyzer.run_analysis(
            geojson_file=args.input,
            csv_output=args.csv_output,
            plot_output=args.plot_output
        )

        print(f"\nAnalysis completed successfully!")
        print(f"Processed {len(results)} glomeruli")
        print(f"Results saved to: {args.csv_output}")
        print(f"Visualization saved to: {args.plot_output}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
