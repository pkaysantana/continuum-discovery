#!/usr/bin/env python3
"""
Safe Python patch script to integrate ESMFold hybrid compute strategy
Fixed Unicode encoding for Windows compatibility
"""

import re

def patch_aminoanalytica_pipeline():
    """Patch the main pipeline file with ESMFold integration"""

    pipeline_file = "agents/aminoanalytica_pipeline.py"

    # Read the original file with UTF-8 encoding
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Patch 1: Add ESMFold filter initialization in __init__
    init_patch = '''        }

        # Initialize ESMFold-based channel filter for hybrid compute
        self.esmfold_filter = ESMFoldChannelFilter()
        self.hybrid_compute_enabled = True
        print(f"[HYBRID-COMPUTE] ESMFold local filtering enabled for credit optimization")'''

    content = content.replace(
        "            'target_type': 'biothreat_countermeasure'\n        }",
        "            'target_type': 'biothreat_countermeasure'\n" + init_patch
    )

    # Patch 2: Add hybrid filtering method before validate_complex_boltz2
    hybrid_method = '''
    async def run_hybrid_esmfold_filtering(self,
                                          sequence_result: Dict[str, Any],
                                          target_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hybrid compute step: Local ESMFold filtering before expensive Amina API calls
        Targets alpha-Helix 8 channel residues (256, 289, 301) for 9/9 hotspot coverage
        """
        if not self.hybrid_compute_enabled:
            return sequence_result

        designed_sequence = sequence_result['designed_sequence']
        design_candidates = sequence_result.get('design_candidates', [])

        print(f"\\n[HYBRID-COMPUTE] Local ESMFold pre-filtering for alpha-Helix 8 targeting")
        print(f"[HYBRID-COMPUTE] Testing {len(design_candidates)} ProteinMPNN candidates locally")

        # Extract sequences from candidates
        candidate_sequences = [designed_sequence]  # Primary sequence
        for candidate in design_candidates[:5]:  # Top 5 additional candidates
            candidate_sequences.append(candidate['sequence'])

        # Run local ESMFold filtering
        deep_pocket_candidates = await self.esmfold_filter.filter_sequences_for_channel_targeting(
            candidate_sequences,
            max_candidates=2  # Forward best 2 to save credits
        )

        if not deep_pocket_candidates:
            print(f"[HYBRID-COMPUTE] WARNING: No candidates passed local filter, using best ProteinMPNN result")
            return sequence_result

        # Select the best candidate that passed local filtering
        best_candidate, penetration_analysis = deep_pocket_candidates[0]

        # Predict hotspot coverage before expensive validation
        predicted_coverage = self.esmfold_filter.predict_final_hotspot_coverage(penetration_analysis)

        print(f"[HYBRID-COMPUTE] SELECTED: Candidate with {predicted_coverage:.1f}% predicted hotspot coverage")
        print(f"[HYBRID-COMPUTE] alpha-Helix 8 contacts: {penetration_analysis['contacts_found']}/3 residues")

        # Update sequence result with filtered candidate
        filtered_result = sequence_result.copy()
        filtered_result['designed_sequence'] = best_candidate
        filtered_result['sequence_length'] = len(best_candidate)
        filtered_result['hybrid_filtering'] = {
            'local_penetration_score': penetration_analysis['penetration_score'],
            'alpha_helix8_contacts': penetration_analysis['contacts_found'],
            'predicted_hotspot_coverage': predicted_coverage,
            'candidates_tested': len(candidate_sequences),
            'passed_local_filter': len(deep_pocket_candidates)
        }

        return filtered_result
'''

    # Find the position to insert the hybrid method (before validate_complex_boltz2)
    boltz2_method_start = content.find("async def validate_complex_boltz2")
    if boltz2_method_start != -1:
        content = content[:boltz2_method_start] + hybrid_method + "\n\n    " + content[boltz2_method_start:]

    # Patch 3: Modify run_complete_pipeline to include hybrid filtering
    pipeline_patch_old = '''            # Step 2: ProteinMPNN sequence design
            print(f"\\n[PIPELINE] Step 2/4: ProteinMPNN sequence design")
            sequence_result = await self.design_sequence_proteinmpnn(backbone_result, design_params)
            pipeline_results['proteinmpnn_result'] = sequence_result

            # Step 3: Boltz-2 complex validation'''

    pipeline_patch_new = '''            # Step 2: ProteinMPNN sequence design
            print(f"\\n[PIPELINE] Step 2/4: ProteinMPNN sequence design")
            sequence_result = await self.design_sequence_proteinmpnn(backbone_result, design_params)
            pipeline_results['proteinmpnn_result'] = sequence_result

            # Step 2.5: Hybrid ESMFold filtering (saves Amina credits)
            print(f"\\n[PIPELINE] Step 2.5/4: Local ESMFold filtering for alpha-Helix 8 targeting")
            filtered_result = await self.run_hybrid_esmfold_filtering(sequence_result, target_info)
            pipeline_results['hybrid_filtering_result'] = filtered_result

            # Step 3: Boltz-2 complex validation (only on filtered candidates)'''

    content = content.replace(pipeline_patch_old, pipeline_patch_new)

    # Patch 4: Use filtered result in Boltz-2 validation
    boltz2_patch_old = "complex_result = await self.validate_complex_boltz2(sequence_result, target_info)"
    boltz2_patch_new = "complex_result = await self.validate_complex_boltz2(filtered_result, target_info)"

    content = content.replace(boltz2_patch_old, boltz2_patch_new)

    # Patch 5: Enhanced ProteinMPNN to generate more candidates for filtering
    proteinmpnn_patch_old = "'num-sequences', '3',"
    proteinmpnn_patch_new = "'num-sequences', '8',  # Generate more candidates for hybrid filtering"

    content = content.replace(proteinmpnn_patch_old, proteinmpnn_patch_new)

    # Write the patched content with UTF-8 encoding
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("SUCCESS: Successfully patched AminoAnalytica pipeline with ESMFold hybrid compute")
    print("SUCCESS: Added local pre-filtering for alpha-Helix 8 channel targeting (256, 289, 301)")
    print("SUCCESS: Enhanced ProteinMPNN to generate 8 candidates for filtering")
    print("SUCCESS: Integrated hybrid step 2.5 between ProteinMPNN and Boltz-2")

if __name__ == "__main__":
    patch_aminoanalytica_pipeline()
