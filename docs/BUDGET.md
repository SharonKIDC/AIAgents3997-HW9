# Project Budget

## LLM Implementation Cost

### Development Cost Summary
| Item | Cost |
|------|------|
| Claude API (development) | $7.74 |
| Local compute | $0.00 |
| Model storage | $0.03 |
| **Total Implementation** | **$7.77** |

### Claude Usage Breakdown
- **Model**: Claude Opus 4.5
- **Input tokens**: ~125,000
- **Output tokens**: ~78,000
- **Development time**: ~4 hours Claude execution

## Server Hosting Costs

### Option 1: Local Deployment (Recommended for Development)
| Resource | Cost |
|----------|------|
| Hardware (existing) | $0.00 |
| Electricity | ~$0.50/month |
| **Monthly Total** | **~$0.50** |

### Option 2: Cloud VPS (Basic)
| Provider | Specs | Monthly Cost |
|----------|-------|--------------|
| DigitalOcean | 4GB RAM, 2 vCPU | $24/month |
| Linode | 4GB RAM, 2 vCPU | $24/month |
| Vultr | 4GB RAM, 2 vCPU | $24/month |

**Note**: Basic VPS lacks GPU, inference will be slower (~5x)

### Option 3: GPU Cloud (Production)
| Provider | GPU | Monthly Cost |
|----------|-----|--------------|
| Lambda Labs | RTX 3090 | ~$150/month |
| RunPod | RTX 3090 | ~$120/month |
| Vast.ai | RTX 3090 | ~$100/month |

### Option 4: Serverless (Pay-per-use)
| Provider | Per Inference | Notes |
|----------|---------------|-------|
| Replicate | ~$0.005/video | Auto-scaling |
| Hugging Face | ~$0.01/video | Easy deployment |
| AWS Lambda | ~$0.02/video | With EFS for models |

## Ongoing LLM Costs

### If using LLM features in production
This project does **NOT** require LLM API calls at inference time.
- DeepFake detection uses local ViT model
- No ongoing Claude/GPT costs for detection

### Optional LLM Features (Future)
| Feature | Cost per Query |
|---------|----------------|
| Video explanation | ~$0.05 (Claude Sonnet) |
| Report generation | ~$0.02 (Claude Haiku) |
| Batch analysis | ~$0.10/10 videos |

## Budget Scenarios

### Scenario 1: Personal/Development
| Item | Monthly |
|------|---------|
| Local hosting | $0.50 |
| No LLM API | $0.00 |
| **Total** | **$0.50/month** |

### Scenario 2: Small Business (100 videos/day)
| Item | Monthly |
|------|---------|
| Serverless (Replicate) | ~$15 |
| Storage (S3) | ~$5 |
| **Total** | **~$20/month** |

### Scenario 3: Enterprise (10,000 videos/day)
| Item | Monthly |
|------|---------|
| Dedicated GPU server | ~$150 |
| Storage & CDN | ~$50 |
| Monitoring | ~$20 |
| **Total** | **~$220/month** |

## ROI Analysis

| Metric | Value |
|--------|-------|
| Development cost | $7.77 |
| Break-even (at $20/mo hosting) | <1 month |
| Detection accuracy | 83%+ |
| Manual review cost saved | ~$0.50/video |

## Recommendations

1. **Start with local deployment** for testing and development
2. **Use serverless** (Replicate/HuggingFace) for initial production
3. **Move to dedicated GPU** when processing >500 videos/day
4. **Consider on-premise** for compliance-sensitive deployments
