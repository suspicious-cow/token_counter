# Billing Validation Log

This document tracks validation of token counter pricing accuracy against actual provider billing data.

## Validation Status Overview

| Provider | Status | Last Validated | Accuracy | Notes |
|----------|--------|----------------|----------|-------|
| OpenAI | ✅ Validated | 2025-01-27 | 100% | Perfect match with billing |
| Gemini | 📋 TBD | - | Unknown | Validation pending billing data review |
| Anthropic | 📋 TBD | - | Unknown | Validation pending billing data review |
| Grok | 🔄 Pending | - | Unknown | Awaiting billing data |

---

## OpenAI Validation ✅

### **Validation Date:** January 27, 2025

### **Test Details:**
- **Prompt:** "Give me the word 'halt' without any formatting or additional text."
- **Model:** gpt-4.1-2025-04-14
- **Response:** "halt"

### **Token Counter Results:**
- **Input tokens:** 21
- **Output tokens:** 1
- **Cached tokens:** 0
- **Calculated cost:** $0.000061

### **OpenAI Official Billing Data:**
```
start_time: 1753574400 (2025-07-27T00:00:00+00:00)
input_tokens: 21
output_tokens: 1
input_cost: $0.000042 (4.2e-05)
output_cost: $0.000008 (8e-06)
total_cost: $0.000050
model: gpt-4.1-2025-04-14
```

### **Discrepancy Analysis:**
- **Token counts:** ✅ Perfect match (21 input, 1 output)
- **Output cost:** ✅ Perfect match ($0.000008)
- **Input cost:** ❌ Discrepancy found ($0.000053 vs $0.000042)

### **Root Cause:**
Token counter was using $2.50/1M for input tokens, but actual billing showed $2.00/1M.

### **Resolution:**
Updated OpenAI pricing configuration:
```python
"input_cost_per_million": 2.00,  # Was 2.50, corrected to match billing
"cached_input_cost_per_million": 0.50,  # 75% discount (was 1.00)
"output_cost_per_million": 8.00  # Confirmed correct
```

### **Official Pricing Verification:**
Confirmed against OpenAI's official GPT-4.1 pricing:
- Input: $2.00 per 1M tokens ✅
- Cached Input: $0.50 per 1M tokens ✅
- Output: $8.00 per 1M tokens ✅

### **Post-Fix Validation:**
- **New calculated cost:** $0.000050
- **Actual billing:** $0.000050
- **Accuracy:** 100% ✅

### **Status:** ✅ **VALIDATED - Perfect accuracy achieved**

---

## OpenAI Re-Validation ✅

### **Re-Validation Date:** January 27, 2025

### **Test Details:**
- **Date**: January 26, 2025 (20:23:28 CDT)
- **API Calls**: 2 requests to OpenAI
- **Model**: gpt-4.1-2025-04-14

### **OpenAI Official Billing Data:**
```
Date: 2025-07-27 (aggregated daily data)
Input tokens: 42
Output tokens: 2
Input cost: $0.000084 (8.4e-05)
Output cost: $0.000016 (1.6e-05)
Total cost: $0.000100
Requests: 2
Model: gpt-4.1-2025-04-14
```

### **Token Counter Validation:**
- **Expected input cost**: 42 × $2.00/1M = $0.000084 ✅ **PERFECT MATCH**
- **Expected output cost**: 2 × $8.00/1M = $0.000016 ✅ **PERFECT MATCH**
- **Expected total cost**: $0.000100 ✅ **PERFECT MATCH**

### **Confirmation:**
- **Token counting**: ✅ 100% accurate
- **Input pricing**: ✅ $2.00/1M confirmed correct
- **Output pricing**: ✅ $8.00/1M confirmed correct
- **Cost calculation**: ✅ Perfect precision match

### **Status:** ✅ **RE-VALIDATED - Continued perfect accuracy with dedicated API keys**

---

## Gemini Validation ⚠️

### **Validation Date:** January 27, 2025

### **Test Details:**
- **Date:** July 23, 2025
- **Model:** gemini-2.5-pro
- **Usage:** 1 API call (per Google Cloud Console graph)

### **Token Counter Results:**
- **Input tokens:** 15
- **Output tokens:** 1
- **Cached tokens:** 0
- **Calculated cost:** $0.000029

### **Google Cloud Billing Data:**
```
Service: Gemini API (AEFD-7695-64FA)
Date: July 23, 2025
Unrounded cost: $0.001718
Model: gemini-2.5-pro (1 usage shown in graph)
```

### **Discrepancy Analysis:**
- **Expected cost:** $0.000029
- **Actual billing:** $0.001718
- **Discrepancy:** 59x higher than expected (5,900% difference)

### **Official Pricing Verification:**
Confirmed token counter configuration matches Google's official Gemini 2.5 Pro pricing:
- Input (≤200K): $1.25/1M ✅
- Output (≤200K): $10.00/1M ✅
- Context caching (≤200K): $0.31/1M ✅

### **Possible Explanations:**
1. **Different token counting:** Google may count tokens differently than reported
2. **Additional features:** Grounding with Google Search ($35/1K requests after free tier)
3. **Context caching storage:** $4.50/1M tokens per hour storage cost
4. **Minimum charges:** Undocumented minimum cost per API request
5. **Processing overhead:** Hidden costs not reflected in published pricing

### **Next Steps:**
- [ ] Gather more detailed Google Cloud Console usage data
- [ ] Check for additional features (search grounding, context caching)
- [ ] Run controlled test with known prompt and verify billing
- [ ] Investigate token counting methodology differences
- [ ] Consider adding adjustment factor or warning for Gemini costs

### **Status:** 📋 **TBD - Validation pending dedicated API key billing data**

**Note**: Previous validation showed significant discrepancy, but this was with mixed API usage. Now using dedicated API keys from .env file for cleaner validation. Awaiting 24-48 hours for billing data to appear in Google Cloud Console.

---

## Anthropic Validation 📋

### **Status:** TBD - Validation pending dedicated API key billing data

**Current Situation:**
- Now using dedicated API keys from .env file for clean billing isolation
- Awaiting 24-48 hours for billing data to appear in Anthropic Console
- Previous mixed usage made validation difficult

**Next Steps:**
- Collect Claude Sonnet 4 billing data from dedicated API key usage
- Compare token counts and costs with actual billing
- Verify cache pricing (ephemeral vs persistent) accuracy
- Validate tiered pricing structure implementation

---

## Grok Validation 🔍

### **Validation Date:** January 27, 2025

### **Test Details:**
- **Date**: July 26, 2025 (20:23:28 CDT)
- **API Key**: Main Key (4cc938a1-2990-42b6-8f14-12fa2ff8c7e)
- **Usage**: Single API call

### **Token Counter Results:**
- **Input tokens**: 21 (19 uncached + 2 cached)
- **Output tokens**: 1
- **Calculated cost**: $0.000074

### **xAI Official Billing Data:**
```
Date: July 26, 2025
Total cost: $0.0023
Token breakdown:
- Reasoning text tokens: 141
- Prompt text tokens: 38
- Cached prompt text tokens: 4
- Completion text tokens: 2
Total actual tokens: 185
```

### **BREAKTHROUGH DISCOVERY:**

**Root Cause Found**: Grok-4 uses **hidden reasoning tokens** not visible in API responses!

**Important Context**: All effort was made to use non-reasoning models for accurate cost comparison across providers. However, Grok-4 does not provide any API parameter or method to disable internal reasoning, making it impossible to achieve true cost parity with other non-reasoning models.

### **Token Analysis:**
- **Visible tokens** (API response): 22 tokens
- **Actual tokens** (xAI billing): 185 tokens
- **Hidden reasoning**: 141 tokens (6.4x multiplier)
- **Token discrepancy**: 8.4x more tokens than visible

### **Cost Validation:**
- **Implied rate**: $0.0023 ÷ 185 tokens × 1M = $12.43 per 1M tokens
- **This suggests**: Pricing rates may be closer to documented, but reasoning tokens create massive cost multiplier

### **Key Findings:**
1. **Hidden processing**: Grok-4 performs internal reasoning not shown to users
2. **Unpredictable costs**: Reasoning token count varies per request
3. **No API visibility**: Reasoning tokens not reported in API usage metadata
4. **Always active**: Internal reasoning appears to be mandatory (cannot be disabled)
5. **Billing transparency**: xAI console shows breakdown, but API doesn't

### **Impact on Token Counter:**
- **Limitation identified**: Cannot predict reasoning token usage
- **Cost accuracy**: Visible token calculations will be 5-10x lower than actual
- **User warning needed**: Grok costs are inherently unpredictable

### **Status:** 🔍 **MYSTERY SOLVED - Hidden reasoning tokens explain cost discrepancy**

**Recommendation**: Add prominent warning about Grok-4's unpredictable reasoning costs

---

## Validation Methodology

### **Standard Validation Process:**
1. **Run controlled test** with known prompt and parameters
2. **Record token counter results** (tokens, costs, model)
3. **Collect official billing data** from provider console/API
4. **Compare token counts** for accuracy
5. **Compare cost calculations** for pricing accuracy
6. **Identify discrepancies** and root causes
7. **Update configuration** if needed
8. **Re-validate** to confirm accuracy

### **Required Data Points:**
- Exact timestamps of API calls
- Token counts (input, output, cached)
- Model names and versions
- Calculated vs actual costs
- Any additional features or charges

### **Acceptance Criteria:**
- **Token counts:** Must match within ±2 tokens (tokenization differences)
- **Cost calculations:** Must match within ±5% (rounding differences)
- **Model identification:** Must match exactly
- **Feature detection:** Must account for all billable features

---

## Notes

- **Validation frequency:** Should be performed monthly or when providers update pricing
- **Documentation:** All discrepancies and resolutions must be documented
- **Configuration updates:** Any pricing changes must be reflected in config.py and README.md
- **User communication:** Significant discrepancies should be noted in documentation with warnings

---

## TODO - Future Validation Tasks

### **High Priority**

- [ ] **OpenAI Web Search Tool Validation**
  - Test web search tool calls with known prompts
  - Measure actual vs expected costs (sub-search multiplier effect)
  - Document cost multiplier patterns (2-5x+ billing)
  - Validate billing dashboard reporting vs actual charges
  - **Goal**: Understand and document unpredictable web search costs

- [ ] **Grok Reasoning Token Investigation**
  - Research if reasoning can be disabled via API parameters
  - Test different prompt types to measure reasoning token variation
  - Document reasoning token multiplier patterns (5-10x+ billing)
  - Investigate if reasoning intensity correlates with prompt complexity
  - **Goal**: Understand and potentially control Grok's hidden reasoning costs

### **Medium Priority**

- [ ] **Gemini Tiered Pricing Edge Cases**
  - Test requests exactly at 200K token threshold
  - Validate tier switching behavior
  - Test with mixed input/output token distributions

- [ ] **Anthropic Cache Type Comparison**
  - Compare ephemeral vs persistent cache costs
  - Validate storage cost calculations (when implemented)
  - Test cache TTL behavior and billing impact

- [ ] **Grok Higher Context Validation**
  - Test requests exactly at 128K token threshold
  - Validate higher context pricing activation
  - Compare standard vs higher context billing

### **Low Priority**

- [ ] **Cross-Provider Token Counting**
  - Compare tokenization differences between providers
  - Document any systematic counting variations
  - Test with various prompt types (code, multilingual, etc.)

- [ ] **Rate Limiting Impact**
  - Test if rate limiting affects token counting accuracy
  - Validate retry logic doesn't double-count tokens

### **Research Tasks**

- [ ] **Provider Billing Delay Patterns**
  - Document actual billing delay times per provider
  - Identify optimal validation timing windows

- [ ] **Caching Behavior Analysis**
  - Test cache hit rates across different prompt patterns
  - Validate cache expiration timing

---

Last updated: January 27, 2025