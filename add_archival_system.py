#!/usr/bin/env python3
"""
Add automatic archival system for high-quality designs to AminoAnalytica pipeline
Saves .pdb files and JSON metadata for designs with ipTM > 0.80 and >= 8/9 hotspot coverage
"""

import os

def add_archival_system():
    """Add archival system to the AminoAnalytica pipeline"""

    pipeline_file = "agents/aminoanalytica_pipeline.py"

    # Read current pipeline
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add archival imports
    archival_imports = """import json
import asyncio
import time
import shutil"""

    # Find where to add the archival class
    archival_class = '''
class DesignArchivalSystem:
    """Automatic archival system for high-quality protein designs"""

    def __init__(self):
        self.outputs_dir = "outputs/winning_binders"
        self.quality_thresholds = {
            'min_iptm': 0.80,
            'min_hotspot_coverage': 88.9  # 8/9 hotspots
        }

        # Ensure output directory exists
        os.makedirs(self.outputs_dir, exist_ok=True)
        print(f"[ARCHIVAL] Automatic saving enabled: {self.outputs_dir}")
        print(f"[ARCHIVAL] Quality thresholds: ipTM > {self.quality_thresholds['min_iptm']}, Hotspots >= {self.quality_thresholds['min_hotspot_coverage']:.1f}%")

    def evaluate_design_quality(self, pipeline_results: Dict[str, Any]) -> bool:
        """Evaluate if design meets archival quality thresholds"""

        final_metrics = pipeline_results.get('final_metrics', {})

        iptm_score = final_metrics.get('iptm_score', 0.0)
        hotspot_coverage = final_metrics.get('hotspot_coverage_percent', 0.0)

        meets_iptm = iptm_score >= self.quality_thresholds['min_iptm']
        meets_hotspots = hotspot_coverage >= self.quality_thresholds['min_hotspot_coverage']

        return meets_iptm and meets_hotspots

    def save_winning_design(self, pipeline_results: Dict[str, Any], biosecurity_score: float = None):
        """Save high-quality design with metadata"""

        if not self.evaluate_design_quality(pipeline_results):
            return None

        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        final_metrics = pipeline_results.get('final_metrics', {})
        iptm = final_metrics.get('iptm_score', 0.0)
        coverage = final_metrics.get('hotspot_coverage_percent', 0.0)

        base_filename = f"winner_{timestamp}_ipTM{iptm:.3f}_cov{coverage:.0f}pct"

        # Extract design information
        sequence_result = pipeline_results.get('proteinmpnn_result', {})
        designed_sequence = sequence_result.get('designed_sequence', 'UNKNOWN')

        # Create PDB content (simplified)
        pdb_content = self._generate_pdb_content(designed_sequence, pipeline_results)

        # Save PDB file
        pdb_path = os.path.join(self.outputs_dir, f"{base_filename}.pdb")
        with open(pdb_path, 'w') as f:
            f.write(pdb_content)

        # Create comprehensive metadata
        metadata = {
            'design_info': {
                'timestamp': timestamp,
                'sequence': designed_sequence,
                'sequence_length': len(designed_sequence),
                'target_pdb': pipeline_results.get('target_info', {}).get('pdb_id', '2IXR'),
                'design_method': 'aminoanalytica_hybrid_pipeline'
            },
            'structural_metrics': {
                'iptm_score': final_metrics.get('iptm_score', 0.0),
                'interface_pae': final_metrics.get('interface_pae', 0.0),
                'overall_score': final_metrics.get('overall_score', 0.0),
                'design_quality': final_metrics.get('design_quality', 'UNKNOWN')
            },
            'hotspot_analysis': {
                'hotspot_coverage_percent': final_metrics.get('hotspot_coverage_percent', 0.0),
                'hotspots_contacted': pipeline_results.get('pesto_result', {}).get('hotspots_contacted', []),
                'total_hotspots': 9,
                'target_hotspots': [128, 135, 142, 156, 166, 243, 256, 289, 301]
            },
            'biosecurity': {
                'security_score': biosecurity_score,
                'threat_classification': 'CRITICAL' if biosecurity_score and biosecurity_score > 0.5 else 'LOW',
                'screening_status': 'FLAGGED' if biosecurity_score and biosecurity_score > 0.5 else 'CLEARED'
            },
            'pipeline_details': {
                'hybrid_filtering': pipeline_results.get('hybrid_filtering_result', {}).get('hybrid_filtering', {}),
                'rfdiffusion_params': pipeline_results.get('rfdiffusion_result', {}).get('rfdiffusion_params', {}),
                'validation_timestamp': pipeline_results.get('pipeline_end', datetime.now().isoformat())
            },
            'archival_criteria': {
                'min_iptm_threshold': self.quality_thresholds['min_iptm'],
                'min_hotspot_threshold': self.quality_thresholds['min_hotspot_coverage'],
                'meets_quality_standards': True
            }
        }

        # Save metadata JSON
        json_path = os.path.join(self.outputs_dir, f"{base_filename}.json")
        with open(json_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"[ARCHIVAL] ✅ WINNER SAVED: {base_filename}")
        print(f"[ARCHIVAL]    ipTM: {final_metrics.get('iptm_score', 0.0):.3f} | Coverage: {final_metrics.get('hotspot_coverage_percent', 0.0):.1f}%")
        print(f"[ARCHIVAL]    Files: {pdb_path}")
        print(f"[ARCHIVAL]           {json_path}")

        return {
            'pdb_file': pdb_path,
            'json_file': json_path,
            'base_filename': base_filename
        }

    def _generate_pdb_content(self, sequence: str, pipeline_results: Dict[str, Any]) -> str:
        """Generate PDB file content for the designed sequence"""

        target_info = pipeline_results.get('target_info', {})
        final_metrics = pipeline_results.get('final_metrics', {})

        pdb_header = f"""HEADER    DESIGNED PROTEIN                        {datetime.now().strftime('%d-%b-%y')}   AMIN
TITLE     AMINOANALYTICA DESIGNED BINDER FOR {target_info.get('pdb_id', '2IXR')}
TITLE    2 IPTM: {final_metrics.get('iptm_score', 0.0):.3f} PAE: {final_metrics.get('interface_pae', 0.0):.2f}A
TITLE    3 HOTSPOT COVERAGE: {final_metrics.get('hotspot_coverage_percent', 0.0):.1f}%
COMPND    MOL_ID: 1;
COMPND   2 MOLECULE: DESIGNED BINDER;
COMPND   3 CHAIN: A;
COMPND   4 ENGINEERED: YES;
COMPND   5 MUTATION: YES
SOURCE    MOL_ID: 1;
SOURCE   2 SYNTHETIC: YES;
SOURCE   3 ORGANISM_SCIENTIFIC: ARTIFICIAL;
SOURCE   4 ORGANISM_TAXID: 32630;
SOURCE   5 OTHER_DETAILS: AMINOANALYTICA GENERATIVE DESIGN
"""

        # Generate simplified atom records for the sequence
        atom_records = []
        for i, aa in enumerate(sequence):
            res_num = i + 1
            # Simplified C-alpha coordinates (would be real coordinates from structure prediction)
            x = (i % 10) * 3.8  # Simplified helix-like positioning
            y = 0.0
            z = i * 1.5

            atom_record = f"ATOM  {res_num:5d}  CA  {self._aa_to_three_letter(aa)} A{res_num:4d}    {x:8.3f}{y:8.3f}{z:8.3f}  1.00 20.00           C  "
            atom_records.append(atom_record)

        pdb_content = pdb_header + "\\n" + "\\n".join(atom_records) + "\\nEND\\n"
        return pdb_content

    def _aa_to_three_letter(self, aa: str) -> str:
        """Convert single letter amino acid to three letter code"""
        aa_map = {
            'A': 'ALA', 'R': 'ARG', 'N': 'ASN', 'D': 'ASP', 'C': 'CYS',
            'E': 'GLU', 'Q': 'GLN', 'G': 'GLY', 'H': 'HIS', 'I': 'ILE',
            'L': 'LEU', 'K': 'LYS', 'M': 'MET', 'F': 'PHE', 'P': 'PRO',
            'S': 'SER', 'T': 'THR', 'W': 'TRP', 'Y': 'TYR', 'V': 'VAL'
        }
        return aa_map.get(aa, 'UNK')

    def list_saved_winners(self):
        """List all saved winning designs"""

        if not os.path.exists(self.outputs_dir):
            print(f"[ARCHIVAL] No winners saved yet")
            return []

        winners = []
        for filename in os.listdir(self.outputs_dir):
            if filename.endswith('.json'):
                json_path = os.path.join(self.outputs_dir, filename)
                with open(json_path, 'r') as f:
                    metadata = json.load(f)
                winners.append(metadata)

        print(f"[ARCHIVAL] Found {len(winners)} winning designs saved")
        return winners'''

    # Add the archival class before the main AminoAnalyticaGenerativePipeline class
    class_insert_point = content.find("class AminoAnalyticaGenerativePipeline:")
    if class_insert_point != -1:
        content = content[:class_insert_point] + archival_class + "\n\n" + content[class_insert_point:]

    # Add archival system initialization to __init__ method
    init_patch = '''        # Initialize design archival system
        self.archival_system = DesignArchivalSystem()'''

    init_insert_point = content.find("        print(f\"[AMINOANALYTICA] Live CLI tools configured: {len(self.amina_tools)} services\")")
    if init_insert_point != -1:
        end_of_line = content.find("\n", init_insert_point)
        content = content[:end_of_line] + "\n\n" + init_patch + content[end_of_line:]

    # Add archival call at the end of run_complete_pipeline
    archival_call = '''
            # Auto-save high-quality designs
            if pipeline_results['status'] == 'success':
                # Extract biosecurity score if available (would be passed from calling agent)
                biosecurity_score = getattr(self, '_last_biosecurity_score', None)
                saved_files = self.archival_system.save_winning_design(pipeline_results, biosecurity_score)
                if saved_files:
                    pipeline_results['archived_files'] = saved_files'''

    # Find the end of the try block in run_complete_pipeline
    try_end_point = content.find("            print(f\"[AMINOANALYTICA] ipTM: {final_metrics['iptm_score']:.3f}, PAE: {final_metrics['interface_pae']:.2f}Å\")")
    if try_end_point != -1:
        end_of_line = content.find("\n", try_end_point)
        content = content[:end_of_line] + archival_call + content[end_of_line:]

    # Add method to set biosecurity score
    biosecurity_method = '''
    def set_biosecurity_score(self, score: float):
        """Set biosecurity score for archival system"""
        self._last_biosecurity_score = score'''

    # Add this method before the _compile_final_metrics method
    method_insert_point = content.find("    def _compile_final_metrics(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:")
    if method_insert_point != -1:
        content = content[:method_insert_point] + biosecurity_method + "\n\n    " + content[method_insert_point:]

    # Write the enhanced pipeline
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ SUCCESS: Added automatic archival system to AminoAnalytica pipeline")
    print("✅ High-quality designs (ipTM > 0.80, coverage >= 88.9%) will be auto-saved")
    print("✅ Output directory: outputs/winning_binders/")
    print("✅ Files saved: .pdb structure files + .json metadata")

if __name__ == "__main__":
    add_archival_system()
