import React, { useState } from "react";
import axios from "axios";

// Create an axios instance with a base URL
const api = axios.create({
    baseURL: "http://127.0.0.1:8000",
});

function App() {
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [resumeFile, setResumeFile] = useState(null);
  const [jobId, setJobId] = useState("");
  const [rankedCandidates, setRankedCandidates] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleError = (message, error) => {
    console.error(message, error);
    alert(message);
  };

  const addJob = async () => {
    if (!jobTitle || !jobDescription) {
      alert("Please enter both job title and description.");
      return;
    }
    setLoading(true);
    try {
      const { data } = await api.post("/add_job/", {
        job_title: jobTitle,
        job_description: jobDescription,
      });
      alert("Job added successfully!");
      setJobId(data.job_id);
    } catch (error) {
      handleError("Failed to add job. Please try again.", error);
    } finally {
      setLoading(false);
    }
  };

  const uploadResume = async () => {
    if (!resumeFile) {
      alert("Please select a file to upload.");
      return;
    }
    if (!jobId) {
      alert("Please create a job before uploading resumes.");
      return;
    }
    const formData = new FormData();
    formData.append("file", resumeFile);
    setLoading(true);
    try {
      await api.post(`/upload_resume/${jobId}`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      alert("Resume uploaded successfully!");
    } catch (error) {
      handleError("Failed to upload resume. Please try again.", error);
    } finally {
      setLoading(false);
    }
  };

  const rankResumes = async () => {
    if (!jobId) {
      alert("Please create a job first.");
      return;
    }
    setLoading(true);
    try {
      const { data } = await api.get(`/get_ranked_candidates_with_feedback/${jobId}`);
      console.log("Ranked candidates:", data.ranked_candidates);
      setRankedCandidates(data.ranked_candidates || []);
    } catch (error) {
      handleError("Failed to rank resumes. Please check the backend.", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>Job and Resume Matching</h1>
      
      {loading && <p>Processing...</p>}

      <section>
        <h2>Create Job</h2>
        <input
          type="text"
          placeholder="Job Title"
          value={jobTitle}
          onChange={(e) => setJobTitle(e.target.value)}
          style={{ marginRight: "10px" }}
        />
        <textarea
          placeholder="Job Description"
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          rows="4"
          cols="50"
          style={{ display: "block", marginBottom: "10px" }}
        />
        <button onClick={addJob}>Add Job</button>
      </section>

      <section style={{ marginTop: "20px" }}>
        <h2>Upload Resumes</h2>
        <input type="file" onChange={(e) => setResumeFile(e.target.files[0])} />
        <button onClick={uploadResume} style={{ marginLeft: "10px" }}>
          Upload Resume
        </button>
      </section>

      <section style={{ marginTop: "20px" }}>
        <h2>Rank Resumes</h2>
        <button onClick={rankResumes}>Rank Candidates</button>
        <div style={{ marginTop: "20px" }}>
          {rankedCandidates.length > 0 ? (
            rankedCandidates.map((candidate, index) => (
              <div
                key={index}
                style={{
                  borderBottom: "1px solid #ccc",
                  paddingBottom: "10px",
                  marginBottom: "10px",
                }}
              >
                <strong>{candidate.resume}</strong> -{" "}
                <span style={{ fontWeight: "bold" }}>
                  Match: {candidate.overall_match_percentage}
                </span>
                <br />
                <span style={{ fontWeight: "bold" }}>
                  Skills:
                </span>{" "}
                {candidate.skills.length > 0
                  ? candidate.skills.join(", ")
                  : "None"}
                <br />
                <span style={{ fontWeight: "bold", color: "red" }}>
                  Feedback:
                </span>{" "}
                {candidate.detailed_feedback ? (
                  <span style={{ color: "red" }}>
                    {candidate.detailed_feedback}
                  </span>
                ) : (
                  <span>No improvements needed.</span>
                )}
              </div>
            ))
          ) : (
            <p>No ranked candidates yet.</p>
          )}
        </div>
      </section>
    </div>
  );
}

export default App;