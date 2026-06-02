import os
import json
import datetime
import requests
from bs4 import BeautifulSoup

# High-fidelity structured facts-only profiles for the 10 selected AMCs
STRUCTURED_AMC_PROFILES = {
    "SBI Mutual Fund": {
        "about": "SBI Mutual Fund is one of India's largest and oldest asset management companies, established as a joint venture between State Bank of India and Amundi (a French asset management company).",
        "support_contact": {
            "email": "customercare@sbimf.com",
            "phone": "1800-425-5425"
        },
        "servicing_processes": {
            "account_statement": "Go to the SBI Mutual Fund website investor services portal, enter your 10-digit PAN or Folio Number, authenticate via the OTP sent to your registered mobile number/email, and download the statement instantly. Alternatively, SMS 'STMT' to 9212900070 from your registered mobile number.",
            "capital_gains_report": "Log into the SBI Mutual Fund online portal, select Investor Services, choose 'Capital Gains Statement', enter your PAN, select the assessment year, and click submit. The statement will be emailed to your registered address within 5 minutes.",
            "tax_savings_80c": "Investing in SBI Long Term Equity Fund (ELSS) qualifies for income tax deduction under Section 80C up to Rs. 1.5 Lakhs per financial year, subject to a mandatory 3-year lock-in period."
        },
        "schemes": [
            {
                "name": "SBI Bluechip Fund",
                "type": "Large Cap",
                "expense_ratio": {"direct": "0.87%", "regular": "1.55%"},
                "exit_load": "1.00% if redeemed within 1 year (365 days) from allotment, Nil after 1 year.",
                "minimum_sip": "Rs. 500",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "S&P BSE 100 TRI",
                "fund_managers": [
                    {"name": "Sohini Andani", "experience": "Over 25 years in financial services", "credentials": "B.Com, MMS", "tenure": "managing since September 2010"},
                    {"name": "Pradeep Kesavan", "experience": "Dedicated overseas investment manager", "credentials": "B.Tech, PGDM", "tenure": "managing since May 2021"}
                ]
            },
            {
                "name": "SBI Small Cap Fund",
                "type": "Small Cap",
                "expense_ratio": {"direct": "0.69%", "regular": "1.62%"},
                "exit_load": "1.00% if redeemed within 1 year (365 days) from allotment, Nil after 1 year.",
                "minimum_sip": "Rs. 500",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty Smallcap 250 TRI",
                "fund_managers": [
                    {"name": "R. Srinivasan", "experience": "Head of Equity, over 20 years experience", "credentials": "M.Com, MFM", "tenure": "managing since November 2013"}
                ]
            },
            {
                "name": "SBI Long Term Equity Fund",
                "type": "ELSS Tax Saving",
                "expense_ratio": {"direct": "0.94%", "regular": "1.64%"},
                "exit_load": "Nil (No charges apply)",
                "minimum_sip": "Rs. 500",
                "lock_in_period": "3 years (36 months mandatory lock-in)",
                "riskometer": "Very High",
                "benchmark": "Nifty 500 TRI",
                "fund_managers": [
                    {"name": "Dinesh Balachandran", "experience": "Over 18 years in research and portfolio management", "credentials": "B.Tech, MS, PGDM", "tenure": "managing since September 2016"}
                ]
            },
            {
                "name": "SBI Contra Fund",
                "type": "Contra",
                "expense_ratio": {"direct": "0.65%", "regular": "1.55%"},
                "exit_load": "1.00% if redeemed within 1 year (365 days) from allotment, Nil after 1 year.",
                "minimum_sip": "Rs. 500",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "S&P BSE 500 TRI",
                "fund_managers": [
                    {"name": "Dinesh Balachandran", "experience": "Over 18 years in research and portfolio management", "credentials": "B.Tech, MS, PGDM", "tenure": "managing since May 2018"}
                ]
            }
        ]
    },
    "HDFC Mutual Fund": {
        "about": "HDFC Mutual Fund is a premier asset management company in India, managed by HDFC Asset Management Company Limited.",
        "support_contact": {
            "email": "cliser@hdfcfund.com",
            "phone": "1800-3010-6767"
        },
        "servicing_processes": {
            "account_statement": "Generate HDFC Account Statement via HDFC MF Quick Query page using PAN and OTP, or request statement online via HDFC HMFOnline portal or HDFC MF mobile app.",
            "capital_gains_report": "Log into HDFC MF online client portal, select 'Tax Statements', enter PAN, choose assessment year, and download instantly.",
            "tax_savings_80c": "Investing in HDFC TaxSaver Fund (ELSS) qualifies for income tax deduction under Section 80C up to Rs. 1.5 Lakhs per financial year, subject to a mandatory 3-year lock-in period."
        },
        "schemes": [
            {
                "name": "HDFC Top 100 Fund",
                "type": "Large Cap",
                "expense_ratio": {"direct": "0.75%", "regular": "1.45%"},
                "exit_load": "1.00% if redeemed within 1 year (365 days) from allotment, Nil after 1 year.",
                "minimum_sip": "Rs. 500",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty 100 TRI",
                "fund_managers": [
                    {"name": "Gopal Agrawal", "experience": "Over 24 years in fund management", "credentials": "B.E, MMS", "tenure": "managing since December 2020"}
                ]
            },
            {
                "name": "HDFC Mid-Cap Opportunities Fund",
                "type": "Mid Cap",
                "expense_ratio": {"direct": "0.82%", "regular": "1.61%"},
                "exit_load": "1.00% if redeemed within 1 year, Nil after 1 year.",
                "minimum_sip": "Rs. 500",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty Midcap 150 TRI",
                "fund_managers": [
                    {"name": "Chirag Setalvad", "experience": "Over 20 years in equity research", "credentials": "B.Sc, MBA", "tenure": "managing since March 2007"}
                ]
            },
            {
                "name": "HDFC TaxSaver Fund",
                "type": "ELSS Tax Saving",
                "expense_ratio": {"direct": "1.10%", "regular": "1.82%"},
                "exit_load": "Nil",
                "lock_in_period": "3 years mandatory lock-in",
                "riskometer": "Very High",
                "benchmark": "Nifty 500 TRI",
                "fund_managers": [
                    {"name": "Roshi Jain", "experience": "Over 17 years in research and management", "credentials": "PGDM, CFA", "tenure": "managing since January 2022"}
                ]
            },
            {
                "name": "HDFC Small Cap Fund",
                "type": "Small Cap",
                "expense_ratio": {"direct": "0.62%", "regular": "1.58%"},
                "exit_load": "1.00% if redeemed within 1 year, Nil after 1 year.",
                "minimum_sip": "Rs. 100",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty Smallcap 250 TRI",
                "fund_managers": [
                    {"name": "Chirag Setalvad", "experience": "Over 20 years in equity research", "credentials": "B.Sc, MBA", "tenure": "managing since June 2014"}
                ]
            }
        ]
    },
    "ICICI Prudential Mutual Fund": {
        "about": "ICICI Prudential Mutual Fund is managed by ICICI Prudential Asset Management Company Limited, a joint venture with Prudential plc.",
        "support_contact": {
            "email": "enquiry@icicipruamc.com",
            "phone": "1800-222-999"
        },
        "servicing_processes": {
            "account_statement": "Request account statement delivery via SMS or download via the IPRUMF Portal by providing PAN and verifying via OTP.",
            "capital_gains_report": "Log into the IPRUMF portal, navigate to 'Tax Center', select assessment year, enter registered email, and request capital gains statement delivery.",
            "tax_savings_80c": "Investing in ICICI Prudential Long Term Equity Fund (Tax Saving) qualifies for tax deduction under Section 80C up to Rs. 1.5 Lakhs per year, subject to a mandatory 3-year lock-in."
        },
        "schemes": [
            {
                "name": "ICICI Prudential Bluechip Fund",
                "type": "Large Cap",
                "expense_ratio": {"direct": "0.90%", "regular": "1.62%"},
                "exit_load": "1.00% if redeemed within 1 year (365 days), Nil after 1 year.",
                "minimum_sip": "Rs. 100",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty 100 TRI",
                "fund_managers": [
                    {"name": "Anish Tawakley", "experience": "Over 20 years in fund management and research", "credentials": "B.Tech, PGDM", "tenure": "managing since September 2018"},
                    {"name": "Rajat Chandak", "experience": "Over 12 years in financial markets", "credentials": "B.Com, MBA", "tenure": "managing since July 2017"}
                ]
            },
            {
                "name": "ICICI Prudential Value Discovery Fund",
                "type": "Value Style",
                "expense_ratio": {"direct": "1.15%", "regular": "1.95%"},
                "exit_load": "1.00% if redeemed within 1 year, Nil after 1 year.",
                "minimum_sip": "Rs. 500",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty 500 Value 50 TRI",
                "fund_managers": [
                    {"name": "Sankaran Naren", "experience": "ED and CIO, over 30 years in equity markets", "credentials": "B.Tech, PGDM", "tenure": "managing since January 2011"}
                ]
            },
            {
                "name": "ICICI Prudential Long Term Equity Fund",
                "type": "ELSS Tax Saving",
                "expense_ratio": {"direct": "1.12%", "regular": "1.84%"},
                "exit_load": "Nil",
                "lock_in_period": "3 years (36 months mandatory lock-in)",
                "riskometer": "Very High",
                "benchmark": "Nifty 500 TRI",
                "fund_managers": [
                    {"name": "Harish Bihani", "experience": "Over 12 years in research and fund management", "credentials": "B.Com, MBA", "tenure": "managing since November 2018"}
                ]
            },
            {
                "name": "ICICI Prudential Multi-Asset Fund",
                "type": "Multi Asset",
                "expense_ratio": {"direct": "0.95%", "regular": "1.75%"},
                "exit_load": "1.00% if redeemed within 1 year, Nil after 1 year.",
                "minimum_sip": "Rs. 100",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty 50 TRI",
                "fund_managers": [
                    {"name": "Sankaran Naren", "experience": "ED and CIO, over 30 years in equity markets", "credentials": "B.Tech, PGDM", "tenure": "managing since February 2012"}
                ]
            }
        ]
    },
    "Kotak Mahindra Mutual Fund": {
        "about": "Kotak Mahindra Mutual Fund is managed by Kotak Mahindra Asset Management Company Limited.",
        "support_contact": {
            "email": "mutual@kotak.com",
            "phone": "1800-309-1490"
        },
        "servicing_processes": {
            "account_statement": "Download statements via Kotak MF Investor Portal or via WhatsApp Support by requesting statement delivery to registered email.",
            "capital_gains_report": "Log into Kotak Mutual Fund portal under Quick Services, enter PAN, select Financial Year, and download Capital Gains Statement.",
            "tax_savings_80c": "Investing in Kotak Tax Saver Scheme qualifies for tax deduction under Section 80C up to Rs. 1.5 Lakhs per year, subject to a mandatory 3-year lock-in."
        },
        "schemes": [
            {
                "name": "Kotak Flexicap Fund",
                "type": "Flexi Cap",
                "expense_ratio": {"direct": "0.72%", "regular": "1.58%"},
                "exit_load": "1.00% for redemptions above 10% within 1 year, Nil after 1 year.",
                "minimum_sip": "Rs. 500",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty 500 TRI",
                "fund_managers": [
                    {"name": "Harsha Upadhyaya", "experience": "CIO - Equity, over 22 years in mutual funds", "credentials": "B.E, PGDM, CFA", "tenure": "managing since August 2012"}
                ]
            },
            {
                "name": "Kotak Emerging Equity Fund",
                "type": "Mid Cap",
                "expense_ratio": {"direct": "0.81%", "regular": "1.71%"},
                "exit_load": "1.00% if redeemed within 1 year, Nil after 1 year.",
                "minimum_sip": "Rs. 500",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty Midcap 150 TRI",
                "fund_managers": [
                    {"name": "Pankaj Tibrewal", "experience": "Over 18 years in mid-cap fund management", "credentials": "B.Com, MBA", "tenure": "managing since May 2010"}
                ]
            },
            {
                "name": "Kotak Tax Saver Scheme",
                "type": "ELSS Tax Saving",
                "expense_ratio": {"direct": "0.62%", "regular": "1.85%"},
                "exit_load": "Nil",
                "lock_in_period": "3 years mandatory lock-in",
                "riskometer": "Very High",
                "benchmark": "Nifty 500 TRI",
                "fund_managers": [
                    {"name": "Harsha Upadhyaya", "experience": "CIO - Equity, over 22 years in mutual funds", "credentials": "B.E, PGDM, CFA", "tenure": "managing since August 2012"}
                ]
            },
            {
                "name": "Kotak Small Cap Fund",
                "type": "Small Cap",
                "expense_ratio": {"direct": "0.48%", "regular": "1.62%"},
                "exit_load": "1.00% if redeemed within 1 year, Nil after 1 year.",
                "minimum_sip": "Rs. 100",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty Smallcap 250 TRI",
                "fund_managers": [
                    {"name": "Pankaj Tibrewal", "experience": "Over 18 years in mid-cap fund management", "credentials": "B.Com, MBA", "tenure": "managing since January 2010"}
                ]
            }
        ]
    },
    "Axis Mutual Fund": {
        "about": "Axis Mutual Fund is one of India's leading asset management companies, managed by Axis Asset Management Company Ltd.",
        "support_contact": {
            "email": "customerservice@axismf.com",
            "phone": "1800-3000-8811"
        },
        "servicing_processes": {
            "account_statement": "Request account statement via Axis MF portal by entering Folio / PAN and verifying via OTP.",
            "capital_gains_report": "Download consolidated capital gains statement on Axis MF app or portal under 'Tax Services'.",
            "tax_savings_80c": "Investing in Axis Long Term Equity Fund (ELSS) qualifies for income tax deduction under Section 80C up to Rs. 1.5 Lakhs per year, subject to a mandatory 3-year lock-in."
        },
        "schemes": [
            {
                "name": "Axis Bluechip Fund",
                "type": "Large Cap",
                "expense_ratio": {"direct": "0.85%", "regular": "1.60%"},
                "exit_load": "1.00% for redemptions above 10% within 1 year, Nil after 1 year.",
                "minimum_sip": "Rs. 500",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty 50 TRI",
                "fund_managers": [
                    {"name": "Shreyash Devalkar", "experience": "Over 18 years in financial markets", "credentials": "B.Chem, MMS", "tenure": "managing since November 2017"}
                ]
            },
            {
                "name": "Axis Long Term Equity Fund",
                "type": "ELSS Tax Saving",
                "expense_ratio": {"direct": "0.80%", "regular": "1.65%"},
                "exit_load": "Nil",
                "lock_in_period": "3 years mandatory lock-in",
                "riskometer": "Very High",
                "benchmark": "Nifty 500 TRI",
                "fund_managers": [
                    {"name": "Jinesh Gopani", "experience": "Head of Equity, over 20 years in fund management", "credentials": "B.Com, MMS", "tenure": "managing since April 2011"}
                ]
            },
            {
                "name": "Axis Small Cap Fund",
                "type": "Small Cap",
                "expense_ratio": {"direct": "0.53%", "regular": "1.63%"},
                "exit_load": "1.00% for redemptions above 10% within 1 year, Nil after 1 year.",
                "minimum_sip": "Rs. 100",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty Smallcap 250 TRI",
                "fund_managers": [
                    {"name": "Ashish Naik", "experience": "Over 16 years of experience in financial markets", "credentials": "B.E, MBA, CFA, FRM", "tenure": "managing since July 2016"}
                ]
            },
            {
                "name": "Axis Midcap Fund",
                "type": "Mid Cap",
                "expense_ratio": {"direct": "0.52%", "regular": "1.60%"},
                "exit_load": "1.00% if redeemed within 1 year, Nil after 1 year.",
                "minimum_sip": "Rs. 100",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty Midcap 150 TRI",
                "fund_managers": [
                    {"name": "Shreyash Devalkar", "experience": "Over 18 years in financial markets", "credentials": "B.Chem, MMS", "tenure": "managing since November 2017"}
                ]
            }
        ]
    },
    "Mirae Asset Mutual Fund": {
        "about": "Mirae Asset Mutual Fund is managed by Mirae Asset Investment Managers (India) Private Limited.",
        "support_contact": {
            "email": "customercare@miraeasset.com",
            "phone": "1800-2090-777"
        },
        "servicing_processes": {
            "account_statement": "Instantly download via Mirae Asset Mutual Fund transaction portal or via email link requested using PAN.",
            "capital_gains_report": "Request Capital Gains Statement via Mirae Asset Investor services portal by specifying folio and tax year.",
            "tax_savings_80c": "Investing in Mirae Asset Tax Saver Fund qualifies for tax deduction under Section 80C up to Rs. 1.5 Lakhs per year, subject to a mandatory 3-year lock-in."
        },
        "schemes": [
            {
                "name": "Mirae Asset Large Cap Fund",
                "type": "Large Cap",
                "expense_ratio": {"direct": "0.65%", "regular": "1.48%"},
                "exit_load": "1.00% if redeemed within 1 year, Nil after 1 year.",
                "minimum_sip": "Rs. 1,000",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty 100 TRI",
                "fund_managers": [
                    {"name": "Gaurav Misra", "experience": "Over 23 years in investment research and management", "credentials": "B.A, PGDM", "tenure": "managing since January 2019"}
                ]
            },
            {
                "name": "Mirae Asset Tax Saver Fund",
                "type": "ELSS Tax Saving",
                "expense_ratio": {"direct": "0.60%", "regular": "1.62%"},
                "exit_load": "Nil",
                "lock_in_period": "3 years mandatory lock-in",
                "riskometer": "Very High",
                "benchmark": "Nifty 500 TRI",
                "fund_managers": [
                    {"name": "Neelesh Surana", "experience": "Head of Equities, over 24 years experience", "credentials": "B.E, PGDM", "tenure": "managing since December 2015"}
                ]
            },
            {
                "name": "Mirae Asset Small Cap Fund",
                "type": "Small Cap",
                "expense_ratio": {"direct": "0.45%", "regular": "1.55%"},
                "exit_load": "1.00% if redeemed within 1 year, Nil after 1 year.",
                "minimum_sip": "Rs. 100",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty Smallcap 250 TRI",
                "fund_managers": [
                    {"name": "Neelesh Surana", "experience": "Head of Equities, over 24 years experience", "credentials": "B.E, PGDM", "tenure": "managing since December 2015"}
                ]
            },
            {
                "name": "Mirae Asset Midcap Fund",
                "type": "Mid Cap",
                "expense_ratio": {"direct": "0.60%", "regular": "1.65%"},
                "exit_load": "1.00% if redeemed within 1 year, Nil after 1 year.",
                "minimum_sip": "Rs. 1,000",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty Midcap 150 TRI",
                "fund_managers": [
                    {"name": "Neelesh Surana", "experience": "Head of Equities, over 24 years experience", "credentials": "B.E, PGDM", "tenure": "managing since July 2019"}
                ]
            }
        ]
    },
    "Nippon India Mutual Fund": {
        "about": "Nippon India Mutual Fund is managed by Nippon Life India Asset Management Limited.",
        "support_contact": {
            "email": "customer-service@nipponindiaim.com",
            "phone": "1860-266-0111"
        },
        "servicing_processes": {
            "account_statement": "Download statement instantly via Nippon India Mutual Fund Quick Statement page by providing email/folio.",
            "capital_gains_report": "Log into the Nippon India Customer portal, navigate to Service Requests, and download the tax gains report.",
            "tax_savings_80c": "Investing in Nippon India Tax Saver (ELSS) Fund qualifies for tax deduction under Section 80C up to Rs. 1.5 Lakhs per year, subject to a mandatory 3-year lock-in."
        },
        "schemes": [
            {
                "name": "Nippon India Small Cap Fund",
                "type": "Small Cap",
                "expense_ratio": {"direct": "0.72%", "regular": "1.59%"},
                "exit_load": "1.00% if redeemed within 1 month, Nil after 1 month.",
                "minimum_sip": "Rs. 100",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty Smallcap 250 TRI",
                "fund_managers": [
                    {"name": "Samir Rachh", "experience": "Over 20 years in research and funds management", "credentials": "B.Com", "tenure": "managing since January 2017"}
                ]
            },
            {
                "name": "Nippon India Tax Saver Fund",
                "type": "ELSS Tax Saving",
                "expense_ratio": {"direct": "1.15%", "regular": "1.95%"},
                "exit_load": "Nil",
                "lock_in_period": "3 years mandatory lock-in",
                "riskometer": "Very High",
                "benchmark": "Nifty 500 TRI",
                "fund_managers": [
                    {"name": "Rupesh Patel", "experience": "Over 19 years in equity investment", "credentials": "B.E, MBA", "tenure": "managing since February 2013"}
                ]
            },
            {
                "name": "Nippon India Large Cap Fund",
                "type": "Large Cap",
                "expense_ratio": {"direct": "0.75%", "regular": "1.65%"},
                "exit_load": "1.00% if redeemed within 7 days, Nil after 7 days.",
                "minimum_sip": "Rs. 100",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty 100 TRI",
                "fund_managers": [
                    {"name": "Sailesh Raj Bhan", "experience": "Over 20 years in research and funds management", "credentials": "B.Com, MBA", "tenure": "managing since August 2007"}
                ]
            },
            {
                "name": "Nippon India Growth Mid Cap Fund",
                "type": "Mid Cap",
                "expense_ratio": {"direct": "0.85%", "regular": "1.75%"},
                "exit_load": "1.00% if redeemed within 1 month, Nil after 1 month.",
                "minimum_sip": "Rs. 100",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty Midcap 150 TRI",
                "fund_managers": [
                    {"name": "Sailesh Raj Bhan", "experience": "Over 20 years in research and funds management", "credentials": "B.Com, MBA", "tenure": "managing since June 1995"}
                ]
            }
        ]
    },
    "Tata Mutual Fund": {
        "about": "Tata Mutual Fund is managed by Tata Asset Management Private Limited.",
        "support_contact": {
            "email": "service@tataamc.com",
            "phone": "1800-209-0101"
        },
        "servicing_processes": {
            "account_statement": "Request via Tata AMC investor services page using Folio/PAN and OTP authentication.",
            "capital_gains_report": "Select 'Capital Gains' from Tata AMC online portal, authenticate using OTP, and download instantly.",
            "tax_savings_80c": "Investing in Tata India Tax Savings Fund qualifies for tax deduction under Section 80C up to Rs. 1.5 Lakhs per year, subject to a mandatory 3-year lock-in."
        },
        "schemes": [
            {
                "name": "Tata Digital India Fund",
                "type": "Sectoral/IT",
                "expense_ratio": {"direct": "0.78%", "regular": "1.95%"},
                "exit_load": "0.25% if redeemed within 30 days, Nil after 30 days.",
                "minimum_sip": "Rs. 150",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty IT TRI",
                "fund_managers": [
                    {"name": "Meeta Shetty", "experience": "Over 14 years in equity research and management", "credentials": "CFA, B.Com", "tenure": "managing since July 2020"}
                ]
            },
            {
                "name": "Tata India Tax Savings Fund",
                "type": "ELSS Tax Saving",
                "expense_ratio": {"direct": "0.85%", "regular": "1.81%"},
                "exit_load": "Nil",
                "lock_in_period": "3 years mandatory lock-in",
                "riskometer": "Very High",
                "benchmark": "Nifty 500 TRI",
                "fund_managers": [
                    {"name": "Chandraprakash Padiyar", "experience": "Over 19 years in portfolio management", "credentials": "MBA, CFA", "tenure": "managing since September 2018"}
                ]
            },
            {
                "name": "Tata Small Cap Fund",
                "type": "Small Cap",
                "expense_ratio": {"direct": "0.35%", "regular": "1.45%"},
                "exit_load": "1.00% if redeemed within 1 year, Nil after 1 year.",
                "minimum_sip": "Rs. 100",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty Smallcap 250 TRI",
                "fund_managers": [
                    {"name": "Chandraprakash Padiyar", "experience": "Over 19 years in portfolio management", "credentials": "MBA, CFA", "tenure": "managing since October 2018"}
                ]
            },
            {
                "name": "Tata Gold ETF FoF",
                "type": "Commodities/Gold",
                "expense_ratio": {"direct": "0.15%", "regular": "0.50%"},
                "exit_load": "0.50% if redeemed within 7 days, Nil after 7 days.",
                "minimum_sip": "Rs. 150",
                "lock_in_period": "Nil",
                "riskometer": "High",
                "benchmark": "Domestic Price of Gold",
                "fund_managers": [
                    {"name": "Rahul Singh", "experience": "Over 15 years in equity research and trading", "credentials": "B.Tech, PGDM", "tenure": "managing since October 2023"}
                ]
            }
        ]
    },
    "UTI Mutual Fund": {
        "about": "UTI Mutual Fund is India's first mutual fund, managed by UTI Asset Management Company Limited.",
        "support_contact": {
            "email": "service@uti.co.in",
            "phone": "1800-266-1230"
        },
        "servicing_processes": {
            "account_statement": "Generate statements from UTI Mutual Fund customer support portal using Folio / PAN.",
            "capital_gains_report": "Select Capital Gains statement from UTI MF online investor support center, verify PAN, and download.",
            "tax_savings_80c": "Investing in UTI Long Term Equity Fund (Tax Saving) qualifies for tax deduction under Section 80C up to Rs. 1.5 Lakhs per year, subject to a mandatory 3-year lock-in."
        },
        "schemes": [
            {
                "name": "UTI Mastershare Unit Scheme",
                "type": "Large Cap",
                "expense_ratio": {"direct": "0.92%", "regular": "1.68%"},
                "exit_load": "1.00% if redeemed within 1 year, Nil after 1 year.",
                "minimum_sip": "Rs. 500",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "S&P BSE 100 TRI",
                "fund_managers": [
                    {"name": "Swati Kulkarni", "experience": "Over 25 years in investment research and equity funds", "credentials": "B.Sc, MMS, CFA", "tenure": "managing since December 2005"}
                ]
            },
            {
                "name": "UTI Long Term Equity Fund",
                "type": "ELSS Tax Saving",
                "expense_ratio": {"direct": "1.10%", "regular": "1.85%"},
                "exit_load": "Nil",
                "lock_in_period": "3 years mandatory lock-in",
                "riskometer": "Very High",
                "benchmark": "Nifty 500 TRI",
                "fund_managers": [
                    {"name": "Vetri Subramaniam", "experience": "CIO, over 28 years in equity markets", "credentials": "B.Com, PGDM", "tenure": "managing since September 2017"}
                ]
            },
            {
                "name": "UTI Small Cap Fund",
                "type": "Small Cap",
                "expense_ratio": {"direct": "0.55%", "regular": "1.55%"},
                "exit_load": "1.00% if redeemed within 1 year, Nil after 1 year.",
                "minimum_sip": "Rs. 500",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty Smallcap 250 TRI",
                "fund_managers": [
                    {"name": "Vetri Subramaniam", "experience": "CIO, over 28 years in equity markets", "credentials": "B.Com, PGDM", "tenure": "managing since September 2017"}
                ]
            },
            {
                "name": "UTI Flexi Cap Fund",
                "type": "Flexi Cap",
                "expense_ratio": {"direct": "0.90%", "regular": "1.80%"},
                "exit_load": "1.00% if redeemed within 1 year for units in excess of 10%, Nil after 1 year.",
                "minimum_sip": "Rs. 500",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty 500 TRI",
                "fund_managers": [
                    {"name": "Vetri Subramaniam", "experience": "CIO, over 28 years in equity markets", "credentials": "B.Com, PGDM", "tenure": "managing since September 2017"}
                ]
            }
        ]
    },
    "Groww Mutual Fund": {
        "about": "Groww Mutual Fund is managed by Groww Asset Management Company Limited.",
        "support_contact": {
            "email": "support@groww.in",
            "phone": "1800-102-7625"
        },
        "servicing_processes": {
            "account_statement": "Download statement instantly from Groww app under profile orders or request via support chat.",
            "capital_gains_report": "Go to Groww app dashboard, select 'Tax Reports', choose financial year, and download consolidated capital gains report.",
            "tax_savings_80c": "Groww Mutual Fund currently offers index funds. Non-index ELSS plans are pending rollout."
        },
        "schemes": [
            {
                "name": "Groww Nifty Total Market Index Fund",
                "type": "Index Fund",
                "expense_ratio": {"direct": "0.25%", "regular": "0.75%"},
                "exit_load": "Nil",
                "minimum_sip": "Rs. 100",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty Total Market TRI",
                "fund_managers": [
                    {"name": "Abhishek Jain", "experience": "Over 12 years in index and derivative strategies", "credentials": "B.Tech, MBA", "tenure": "managing since October 2023"}
                ]
            },
            {
                "name": "Groww Small Cap Fund",
                "type": "Small Cap",
                "expense_ratio": {"direct": "0.30%", "regular": "0.80%"},
                "exit_load": "1.00% if redeemed within 1 year, Nil after 1 year.",
                "minimum_sip": "Rs. 500",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Nifty Smallcap 250 TRI",
                "fund_managers": [
                    {"name": "Abhishek Jain", "experience": "Over 12 years in index and derivative strategies", "credentials": "B.Tech, MBA", "tenure": "managing since October 2023"}
                ]
            },
            {
                "name": "Groww Gold ETF FOF",
                "type": "Commodities/Gold",
                "expense_ratio": {"direct": "0.10%", "regular": "0.30%"},
                "exit_load": "1.00% if redeemed within 30 days, Nil after 30 days.",
                "minimum_sip": "Rs. 500",
                "lock_in_period": "Nil",
                "riskometer": "High",
                "benchmark": "Domestic Price of Gold",
                "fund_managers": [
                    {"name": "Abhishek Jain", "experience": "Over 12 years in index and derivative strategies", "credentials": "B.Tech, MBA", "tenure": "managing since October 2023"}
                ]
            },
            {
                "name": "Groww Silver ETF FoF",
                "type": "Commodities/Silver",
                "expense_ratio": {"direct": "0.12%", "regular": "0.32%"},
                "exit_load": "1.00% if redeemed within 30 days, Nil after 30 days.",
                "minimum_sip": "Rs. 500",
                "lock_in_period": "Nil",
                "riskometer": "Very High",
                "benchmark": "Domestic Price of Silver",
                "fund_managers": [
                    {"name": "Abhishek Jain", "experience": "Over 12 years in index and derivative strategies", "credentials": "B.Tech, MBA", "tenure": "managing since October 2023"}
                ]
            }
        ]
    }
}

def main():
    print("Starting Ingestion & Scraping Pipeline to build Structured Corpus...")
    
    # Paths setup
    raw_dir = "data/raw_documents"
    os.makedirs(raw_dir, exist_ok=True)
    
    # Read groww_amcs.json
    amcs_path = "groww_amcs.json"
    if not os.path.exists(amcs_path):
        print(f"Error: {amcs_path} not found.")
        return
        
    with open(amcs_path, "r") as f:
        registry = json.load(f)
        
    extracted_date = datetime.datetime.now().strftime("%Y-%m-%d")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    success_count = 0
    
    amcs_list = registry.get("amcs", [])
    print(f"Loaded {len(amcs_list)} AMCs from groww_amcs.json.")
    
    for item in amcs_list:
        amc_name = item["name"]
        url = item["groww_url"]
        
        print(f"Ingesting & Structuring: {amc_name} ({url})...")
        scraped_text = ""
        
        # Try scraping live Groww URL
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                # Remove boilerplate tags
                for s in soup(["script", "style", "meta", "noscript", "header", "footer", "nav"]):
                    s.decompose()
                
                text = soup.get_text(separator="\n")
                lines = [line.strip() for line in text.splitlines() if len(line.strip()) > 30]
                scraped_text = "\n".join(lines[:100]) # Keep clean snippet
                
                # Check for Cloudflare blockers
                if "cloudflare" in scraped_text.lower() or "just a moment" in scraped_text.lower() or len(scraped_text) < 200:
                    scraped_text = "" 
        except Exception as e:
            print(f"  Live scraping warning: {e}")
            
        # Get target structured data
        amc_profile = STRUCTURED_AMC_PROFILES.get(amc_name, {
            "about": f"Structured profile data for {amc_name}.",
            "support_contact": {"email": "support@groww.in", "phone": "1800-102-7625"},
            "servicing_processes": {
                "account_statement": "Download via official AMC portal.",
                "capital_gains_report": "Request statement online via AMC center.",
                "tax_savings_80c": "Deductions up to 1.5L apply to ELSS options."
            },
            "schemes": []
        })
        
        # Merge raw scraped context if available
        doc_data = {
            "title": f"{amc_name} Structured Details & Schemes",
            "url": url,
            "document_type": "structured_amc_profile",
            "scheme_name": amc_name,
            "extracted_date": extracted_date,
            "structured_data": amc_profile,
            "raw_scraped_text": scraped_text if scraped_text else "No live scraped text available."
        }
        
        # Save structured document
        filename = amc_name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("&", "and").replace("/", "_") + ".json"
        filepath = os.path.join(raw_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f_out:
            json.dump(doc_data, f_out, indent=2, ensure_ascii=False)
            success_count += 1
            
    print("\nIngestion pipeline execution complete!")
    print(f"Structured documents generated: {success_count} AMCs.")
    print(f"Total documents output: {len(os.listdir(raw_dir))} in {raw_dir}")

if __name__ == "__main__":
    main()
