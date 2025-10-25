def match_keywords(jd_keywords, resume_keywords):
    matched = [word for word in jd_keywords if word in resume_keywords]
    missing = [word for word in jd_keywords if word not in resume_keywords]
    return matched, missing
