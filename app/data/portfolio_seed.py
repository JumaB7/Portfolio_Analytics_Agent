"""Local fallback dataset — keep aligned with PortfolioAPI PortfolioAnalyticsData."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def create_portfolio_seed() -> dict[str, Any]:
    return {
        "sourceLabel": "Portfolio site content shared with the AI agent",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "yearsExperience": 4,
        "owner": {
            "name": "Jumari Blignaut",
            "role": "Full-Stack Software Engineer",
            "location": "Potchefstroom, South Africa",
            "summary": (
                "Full-Stack Software Engineer with nearly four years of professional "
                "experience developing and maintaining web applications across financial "
                "technology, higher education and fleet telematics. Experienced in frontend "
                "and backend development, with a strong technical foundation in C#, .NET, "
                "Angular, TypeScript and SQL. Holds a Bachelor of Engineering in Computer "
                "and Electronic Engineering from North-West University, completed with distinction."
            ),
            "highlights": [
                {
                    "label": "Education",
                    "value": "BEng Computer & Electronic Engineering — NWU (Distinction)",
                },
                {"label": "Experience", "value": "Nearly 4 years professional"},
                {"label": "Focus", "value": "Angular · ASP.NET · SQL Server · Azure"},
                {"label": "Based in", "value": "Potchefstroom, South Africa"},
            ],
        },
        "contact": {"email": "jumablignaut@gmail.com"},
        "skillGroups": [
            {
                "title": "Frontend",
                "skills": ["Angular", "TypeScript", "JavaScript", "HTML", "CSS", "Tailwind"],
            },
            {
                "title": "Backend",
                "skills": ["C#", "ASP.NET Core", "PHP", "REST APIs", "Node.js"],
            },
            {
                "title": "Databases",
                "skills": ["SQL Server", "SQL", "Database design"],
            },
            {
                "title": "Tools & Platforms",
                "skills": ["Git", "Azure", "Visual Studio", "VS Code", "Highcharts"],
            },
        ],
        "experience": [
            {
                "title": "Software Engineer",
                "organization": "Matogen",
                "dates": "01/2023 – Present",
                "location": "Potchefstroom, South Africa",
                "description": (
                    "Contributed to the development and maintenance of software solutions "
                    "across financial technology, higher education, fleet telematics and "
                    "workflow automation."
                ),
                "technologies": [
                    "Angular",
                    "C#",
                    ".NET",
                    "TypeScript",
                    "Highcharts",
                    "NestJS",
                    "SQL",
                    "Azure",
                ],
            },
            {
                "title": "Bachelor of Engineering in Computer and Electronic Engineering",
                "organization": "North-West University",
                "dates": "2019 – 2022",
                "location": "Potchefstroom, South Africa",
                "description": "Academic achievement: Graduated with Distinction.",
                "technologies": ["Engineering"],
            },
        ],
        "projects": [
            {
                "id": "veld-supply",
                "name": "Veld Supply",
                "category": "Full-stack web applications",
                "technologies": ["Angular", "ASP.NET Core", "SQL Server", "Azure"],
                "status": "completed",
                "startDate": None,
                "endDate": None,
                "description": (
                    "Standalone South African e-commerce application with its own "
                    "ASP.NET Core API and SQL Server database."
                ),
            },
            {
                "id": "accountant-app",
                "name": "Accountant App",
                "category": "Mobile applications",
                "technologies": ["Angular", "ASP.NET Core", "SQL Server", "Mobile"],
                "status": "in-progress",
                "startDate": None,
                "endDate": None,
                "description": (
                    "Accounting platform with a shared backend for an admin dashboard "
                    "web app and a mobile application."
                ),
            },
            {
                "id": "portfolio-dashboard",
                "name": "Portfolio Dashboard",
                "category": "AI/data analytics",
                "technologies": ["Angular", "Highcharts", "ASP.NET Core", "SQL Server"],
                "status": "in-progress",
                "startDate": None,
                "endDate": None,
                "description": (
                    "Data dashboard inside this portfolio, powered by the portfolio API "
                    "and analytics agent."
                ),
            },
        ],
    }
