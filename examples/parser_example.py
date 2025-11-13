"""
Example: Using the VOACAP Binary Parser

This example demonstrates how to load and inspect VOACAP coefficient data
from the binary data files.
"""

from pathlib import Path
from dvoacap.voacap_parser import VoacapParser, load_month

# Get the data directory
repo_root = Path(__file__).parent.parent
data_dir = repo_root / "DVoaData"


def main():
    print("=" * 70)
    print("VOACAP Binary Parser Example")
    print("=" * 70)
    print()

    # Example 1: Load data for January (month 1)
    print("Example 1: Loading January coefficient data")
    print("-" * 70)
    coeff_data, f2_data = load_month(str(data_dir), month=1)

    print(f"✓ Successfully loaded January data files")
    print(f"  - Coefficient file: Coeff01.dat")
    print(f"  - F2 frequency file: FOF2CCIR01.dat")
    print()

    # Example 2: Inspect data structure
    print("Example 2: Inspecting data structures")
    print("-" * 70)
    print(f"IKIM array shape (map indices):       {coeff_data.ikim.shape}")
    print(f"DUD array shape (noise parameters):   {coeff_data.dud.shape}")
    print(f"FAM array shape (noise factors):      {coeff_data.fam.shape}")
    print(f"SYS array shape (system loss):        {coeff_data.sys.shape}")
    print(f"Fixed coeff P shape:                  {coeff_data.fixed_coeff.P.shape}")
    print(f"Fixed coeff ABP shape:                {coeff_data.fixed_coeff.ABP.shape}")
    print(f"F2 coefficients shape:                {f2_data.xf2cof.shape}")
    print()

    # Example 3: Get data summary
    print("Example 3: Data summary with value ranges")
    print("-" * 70)
    summary = VoacapParser.get_data_summary(coeff_data)

    print(f"ANEW coefficients (F1 layer):         {summary['anew']}")
    print(f"BNEW coefficients (F1 layer):         {summary['bnew']}")
    print(f"ACHI coefficients (zenith angle):     {summary['achi']}")
    print(f"BCHI coefficients (zenith angle):     {summary['bchi']}")
    print(f"DUD value range:                      {summary['dud_range']}")
    print()

    # Example 4: Load multiple months
    print("Example 4: Loading data for all 12 months")
    print("-" * 70)
    for month in range(1, 13):
        try:
            coeff, f2 = VoacapParser.load_monthly_data(data_dir, month)
            month_name = [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ][month - 1]
            print(f"✓ {month_name:3s} (Month {month:2d}): "
                  f"IKIM[0,0]={coeff.ikim[0, 0]:2d}, "
                  f"ANEW[0]={coeff.anew[0]:7.4f}")
        except Exception as e:
            print(f"✗ Month {month:2d}: Error - {e}")
    print()

    # Example 5: Access specific coefficient arrays
    print("Example 5: Accessing specific coefficient data")
    print("-" * 70)
    print(f"First row of IKIM (variable map indices):")
    print(f"  {coeff_data.ikim[0, :]}")
    print()
    print(f"XFMCF shape (M3000 coefficients):     {coeff_data.xfm3cf.shape}")
    print(f"XESMCF shape (Es median coefficients): {coeff_data.xesmcf.shape}")
    print(f"XESLCF shape (Es lower coefficients):  {coeff_data.xeslcf.shape}")
    print(f"XESUCF shape (Es upper coefficients):  {coeff_data.xesucf.shape}")
    print(f"XERCOF shape (E layer coefficients):   {coeff_data.xercof.shape}")
    print()

    # Example 6: Compare January vs July
    print("Example 6: Seasonal variation (January vs July)")
    print("-" * 70)
    jan_coeff, jan_f2 = VoacapParser.load_monthly_data(data_dir, 1)
    jul_coeff, jul_f2 = VoacapParser.load_monthly_data(data_dir, 7)

    print(f"January ANEW[0]: {jan_coeff.anew[0]:.6f}")
    print(f"July    ANEW[0]: {jul_coeff.anew[0]:.6f}")
    print(f"Difference:      {abs(jul_coeff.anew[0] - jan_coeff.anew[0]):.6f}")
    print()

    jan_dud_mean = jan_coeff.dud.mean()
    jul_dud_mean = jul_coeff.dud.mean()
    print(f"January DUD mean: {jan_dud_mean:.6f}")
    print(f"July    DUD mean: {jul_dud_mean:.6f}")
    print(f"Difference:       {abs(jul_dud_mean - jan_dud_mean):.6f}")
    print()

    print("=" * 70)
    print("Parser example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
