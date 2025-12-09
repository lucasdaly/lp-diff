import os
import sys
sys.path.append('./src/lp-diff/core')

from validation import run_full_validation

def main():
    print("Starting validation against ground truth XML files...")
    print("=" * 60)
    
    try:
        results = run_full_validation()
        
        # Print detailed results for poor performing tests
        print("\n" + "=" * 60)
        print("DETAILED ANALYSIS")
        print("=" * 60)
        
        poor_performers = [r for r in results if r['f1_score'] < 0.8]
        good_performers = [r for r in results if r['f1_score'] >= 0.8]
        
        if poor_performers:
            print(f"\n⚠️  {len(poor_performers)} tests need attention (F1 < 0.8):")
            for result in poor_performers:
                print(f"   {result['test_name']}: F1={result['f1_score']:.3f} "
                      f"(P={result['precision']:.3f}, R={result['recall']:.3f})")
        
        if good_performers:
            print(f"\n✅ {len(good_performers)} tests performing well (F1 >= 0.8):")
            for result in good_performers:
                print(f"   {result['test_name']}: F1={result['f1_score']:.3f}")
        
        # Summary statistics
        if results:
            best = max(results, key=lambda x: x['f1_score'])
            worst = min(results, key=lambda x: x['f1_score'])
            
            print(f"\n📊 SUMMARY:")
            print(f"   Best:  {best['test_name']} (F1: {best['f1_score']:.3f})")
            print(f"   Worst: {worst['test_name']} (F1: {worst['f1_score']:.3f})")
            print(f"   Total tests: {len(results)}")
        
    except Exception as e:
        print(f"Error running validation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()