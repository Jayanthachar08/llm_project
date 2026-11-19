# Project Overview: CampusFlow AI

## 1. Project Title
**CampusFlow AI: An LLM-Powered Academic Task Planning and Deadline Management System**

## 2. Official Project Description
CampusFlow AI is an LLM-powered system that converts academic announcements, assignments, and schedules into organized tasks. It identifies deadlines, prioritizes tasks, detects scheduling conflicts, and generates personalized study plans. It also provides reminders, progress tracking, and dynamic schedule updates, helping students manage responsibilities and avoid missed deadlines.

## 3. Problem Statement & Motivation
College students receive announcements across disparate formats: WhatsApp messages, portal circulars, scanned PDFs, classroom circulars, and exam timetables. Manually tracking multiple submission instructions, extracting deadlines, balancing study hours around fixed college timetables, and adjusting to unexpected schedule changes is mentally taxing and prone to missed deadlines.

Traditional task managers require students to manually type all task details, dates, and durations. They have no natural-language intelligence to understand academic circulars, nor do they calculate dynamic academic priority or generate collision-free study timetables.

## 4. Objectives
1. Understand unstructured academic announcements via Google Gemini 3.5 Flash-Lite (`gemini-3.5-flash-lite`) and the modern Google GenAI SDK (`google-genai`).
2. Separate submission deadlines from examination/event dates without fabrication.
3. Augment extraction with Retrieval-Augmented Generation (RAG) using persistent ChromaDB vector storage.
4. Enforce a 4-layer guardrail pipeline (input, output, human-in-the-loop, scheduling).
5. Deterministically prioritize tasks using a weighted academic formula ($P = 0.40U + 0.25I + 0.20D + 0.15W$).
6. Detect schedule overlaps, competing deadlines, and insufficient study time.
7. Generate personalized daily and weekly study timetables with enforced breaks.
8. Support dynamic rescheduling that preserves completed work.
9. Deliver automated reminders via APScheduler and provide real-time progress analytics.
