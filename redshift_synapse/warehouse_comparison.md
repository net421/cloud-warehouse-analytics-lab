# Redshift vs Azure Synapse

| Concern | Redshift | Synapse dedicated SQL |
|---|---|---|
| Distribution | DISTKEY / EVEN / ALL | HASH / ROUND_ROBIN / REPLICATE |
| Ordering/storage | sort keys | clustered columnstore |
| Fast creation | CTAS | CTAS |
| Lake access | Spectrum / S3 | serverless SQL / ADLS |

Use hash distribution on high-volume join keys when skew is controlled, and replicate small dimensions.
