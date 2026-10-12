# Task 4: Sentiment Analysis of WHO Disease Outbreak Announcements

## 1. Project Overview

This analysis applies VADER (Valence Aware Dictionary and sEntiment Reasoner), a rule-based natural language processing tool, to text from World Health Organization (WHO) Disease Outbreak News announcements.

The objective is to explore the linguistic sentiment expressed in outbreak-report text as a complementary text-analysis exercise. The results are not a measure of public opinion, clinical severity, or outbreak probability.

## 2. Dataset

- **Records analyzed:** 493
- **Source:** WHO Disease Outbreak News announcements.
- **Additional text enrichment:** Extracted text from 30 sampled WHO article pages was merged into matching announcement records where available.
- **Records enriched with scraped article text:** 30
- **Scoring tool:** VADER SentimentIntensityAnalyzer.

The 30 scraped article texts were matched to existing announcements; they are not counted as 30 additional independent announcements.

## 3. Methodology

VADER assigns a compound sentiment score between -1 and +1 by combining lexical sentiment and contextual rules.

The following standard thresholds were used to classify the scores:

- **Negative:** compound score <= -0.05
- **Neutral:** compound score > -0.05 and < +0.05
- **Positive:** compound score >= +0.05

These labels describe the text's estimated linguistic polarity. They do not establish whether an announcement is factually good or bad, nor do they measure the emotional state of readers.

## 4. Results

| Sentiment classification | Records | Percentage |
|---|---:|---:|
| Negative | 288 | 58.42% |
| Neutral | 17 | 3.45% |
| Positive | 188 | 38.13% |
| **Total** | **493** | **100.00%** |

### Compound score summary

- **Mean compound score:** -0.1701
- **Median compound score:** -0.4019
- **Minimum compound score:** -0.9992
- **Maximum compound score:** 0.9998

## 5. Interpretation

The distribution describes the polarity VADER detected in the language of WHO outbreak announcements. Negative classifications can arise from terms associated with illness, transmission, deaths, and other adverse events. Such terminology is common in factual public-health reporting.

Consequently, a high proportion of negative classifications should not be interpreted as evidence of negative public opinion or as a direct indicator of disease severity. Likewise, positive classifications do not mean an outbreak is improving or that the reported event poses little risk.

The findings are best treated as exploratory text-analysis results that complement, rather than replace, epidemiological data and expert interpretation.

## 6. Visualizations

The following interactive HTML visualizations were generated:

1. `sentiment_distribution.html` — counts of negative, neutral, and positive classifications.
2. `sentiment_compound_distribution.html` — distribution of compound sentiment scores.
3. `sentiment_by_year.html` — sentiment classifications grouped by publication year.

These files are located in the project's `reports/` directory.

## 7. Limitations

1. **Domain limitation:** VADER is a general-purpose sentiment tool, not a public-health-specific language model.
2. **Context limitation:** Technical disease terminology and descriptions of severe events may be classified as negative even when written objectively.
3. **Interpretation limitation:** Sentiment labels are not measures of public opinion, outbreak probability, clinical severity, or response effectiveness.
4. **Sampling limitation:** The 30 scraped article pages represent a subset of the announcement records, not a separate representative sample of all WHO reporting.
5. **Validation limitation:** The automated labels have not been independently validated against a manually annotated public-health text dataset.
6. **Temporal limitation:** Differences between years may reflect changes in topics, reporting volume, or wording rather than changes in real-world disease conditions.

## 8. Conclusion

VADER provided a reproducible baseline for classifying the linguistic polarity of 493 WHO outbreak announcement records. The results demonstrate how text-processing methods can add a descriptive text-analysis layer to a multisource public-health intelligence project.

Any operational use would require domain-specific validation and careful separation of text sentiment from epidemiological risk assessment.

## 9. Reproducibility

Primary results: `data/processed/who_sentiment_results.csv`

Related outputs:
- `reports/sentiment_analysis_summary.txt`
- `reports/sentiment_distribution.html`
- `reports/sentiment_compound_distribution.html`
- `reports/sentiment_by_year.html`

Generated on: 2026-10-12
