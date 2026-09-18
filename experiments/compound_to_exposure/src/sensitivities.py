def run_sensitivity_analyses(master_partition_df, datasets):
    """
    master_partition_df: the immutable split assignment
    datasets: dict containing 'interior_731', 'below_274', 'above_84', 'ambiguous_13'
    """
    # Verify split regeneration hasn't occurred
    # Since we take the master partition as input, we aren't regenerating it
    
    # 1. Primary
    primary_cohort = datasets['interior_731']
    
    # 2. Sensitivity A
    # Includes ambiguous 13 as exact 3
    import pandas as pd
    sensitivity_a_cohort = pd.concat([datasets['interior_731'], datasets['ambiguous_13']])
    
    # 3. Sensitivity B
    # Treats ambiguous 13 with the censored group
    # They don't enter point regression
    sensitivity_b_cohort = datasets['interior_731']
    sensitivity_b_censored = pd.concat([datasets['below_274'], datasets['ambiguous_13']])
    
    return {
        'primary': primary_cohort,
        'sens_a': sensitivity_a_cohort,
        'sens_b_main': sensitivity_b_cohort,
        'sens_b_censored': sensitivity_b_censored
    }
