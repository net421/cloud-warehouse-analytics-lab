from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUTPUT_DIR=ROOT/"outputs"

def validate_outputs(output_dir=OUTPUT_DIR):
    output_dir=Path(output_dir)
    orders=pd.read_csv(output_dir/"mart_order_fulfillment.csv")
    carriers=pd.read_csv(output_dir/"mart_carrier_performance.csv")
    quality=pd.read_csv(output_dir/"data_quality_report.csv")
    return [
        ("order_output_non_empty",len(orders)>0,len(orders)),
        ("order_id_unique",orders["order_id"].is_unique,orders["order_id"].nunique()),
        ("service_metrics_in_range",orders["unit_fill_rate"].between(0,1).all(),"fill rate"),
        ("otif_logic",((orders["otif_flag"]<=orders["on_time_flag"]) &
                       (orders["otif_flag"]<=orders["complete_order_flag"])).all(),"OTIF components"),
        ("carrier_output_non_empty",len(carriers)>0,len(carriers)),
        ("warehouse_quality_report",(quality["status"]=="PASS").all(),(quality["status"]=="PASS").sum()),
    ]

if __name__=="__main__":
    results=validate_outputs()
    for name,ok,detail in results:
        print(f"{'PASS' if ok else 'FAIL':4} {name}: {detail}")
    if not all(r[1] for r in results):
        raise SystemExit(1)
