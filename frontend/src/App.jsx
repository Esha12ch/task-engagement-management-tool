import { useState, useEffect } from "react";
import axios from "axios";
import {
  BrowserRouter,
  Routes,
  Route,
  useNavigate
} from "react-router-dom";


/* =========================================================
   LOGIN
========================================================= */

function Login() {
  const [role, setRole] = useState("TEAM_MEMBER");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        "http://127.0.0.1:8001/auth/login",
        {
          email: email,
          password: password,
        }
      );

      const token = response.data.access_token;

      /* Save token */

      localStorage.setItem(
        "access_token",
        token
      );

      /* Get actual user information from backend */

      const userResponse = await axios.get(
        "http://127.0.0.1:8001/auth/me",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      /* Save actual role and name */

      localStorage.setItem(
        "user_role",
        userResponse.data.role
      );

      localStorage.setItem(
        "user_name",
        userResponse.data.name
      );

      navigate("/dashboard");

    } catch (error) {
      if (error.response) {
        alert(
          error.response.data.detail ||
          "Login failed"
        );
      } else {
        alert(
          "Unable to connect to backend"
        );
      }
    }
  };

  return (
    <div className="login-container">

      <div className="login-card">

        <h1>Task Management Tool</h1>

        <p className="subtitle">
          Sign in to your account
        </p>

        <form onSubmit={handleLogin}>

          {/* ROLE */}

          <label>
            Login As
          </label>

          <select
            value={role}
            onChange={(e) =>
              setRole(e.target.value)
            }
          >
            <option value="ADMIN">
              Admin
            </option>

            <option value="MANAGER">
              Manager
            </option>

            <option value="TEAM_MEMBER">
              Team Member
            </option>
          </select>


          {/* EMAIL */}

          <label>
            Email
          </label>

          <input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
            required
          />


          {/* PASSWORD */}

          <label>
            Password
          </label>

          <input
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
            required
          />


          {/* LOGIN */}

          <button type="submit">
            Login
          </button>

        </form>

      </div>

    </div>
  );
}


/* =========================================================
   DASHBOARD
========================================================= */

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const role =
    localStorage.getItem("user_role");

  const userName =
    localStorage.getItem("user_name");


  /* LOGOUT */

  const logout = () => {
    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "user_role"
    );

    localStorage.removeItem(
      "user_name"
    );

    navigate("/");
  };


  /* LOAD DASHBOARD */

  const loadDashboard = async () => {
    try {

      const token =
        localStorage.getItem(
          "access_token"
        );

      if (!token) {
        navigate("/");
        return;
      }

      const response =
        await axios.get(
          "http://127.0.0.1:8001/dashboard/summary",
          {
            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );

      setSummary(
        response.data
      );

    } catch (error) {

      if (
        error.response &&
        error.response.status === 401
      ) {
        localStorage.removeItem(
          "access_token"
        );

        localStorage.removeItem(
          "user_role"
        );

        localStorage.removeItem(
          "user_name"
        );

        navigate("/");
        return;
      }

      setError(
        "Unable to load dashboard data"
      );
    }
  };


  useEffect(() => {
    loadDashboard();
  }, []);


  /* ERROR */

  if (error) {
    return (
      <div
        style={{
          padding: "40px"
        }}
      >

        <h1>
          Dashboard
        </h1>

        <p>
          {error}
        </p>

        <button
          onClick={logout}
        >
          Logout
        </button>

      </div>
    );
  }


  /* LOADING */

  if (!summary) {
    return (
      <div
        style={{
          padding: "40px"
        }}
      >

        <h1>
          Dashboard
        </h1>

        <p>
          Loading dashboard...
        </p>

      </div>
    );
  }


  return (
    <div
      style={{
        padding: "40px"
      }}
    >

      {/* TITLE */}

      <h1>
        Dashboard
      </h1>


      {/* USER INFORMATION */}

      <p>
        Welcome,{" "}
        <strong>
          {userName || "User"}
        </strong>
      </p>

      <p>
        Role:{" "}
        <strong>
          {role || "Unknown"}
        </strong>
      </p>


      {/* NAVIGATION */}

      <div className="navigation-buttons">

        <button
          onClick={() =>
            navigate("/dashboard")
          }
        >
          Dashboard
        </button>

        <button
          onClick={() =>
            navigate("/tasks")
          }
        >
          Tasks
        </button>

        {(role === "ADMIN" ||
          role === "MANAGER") && (
          <button
            onClick={() =>
              navigate("/engagements")
            }
          >
            Engagements
          </button>
        )}

        {role === "ADMIN" && (
  <button
    onClick={() =>
      navigate("/services")
    }
  >
    Services
  </button>
)}

        {role === "ADMIN" && (
          <button
            onClick={() =>
              navigate("/clients")
            }
          >
            Clients
          </button>
        )}

        <button
          onClick={logout}
        >
          Logout
        </button>

      </div>


      {/* =================================================
          ROLE BASED CONTROLS
      ================================================= */}

      <div className="role-section">


        {/* ADMIN */}

        {role === "ADMIN" && (
  <div>
    <h2>Admin Controls</h2>

    <p>
      Manage users, clients, service types and task templates.
    </p>

    <button onClick={() => navigate("/users")}>
      Manage Users
    </button>

    <button onClick={() => navigate("/clients")}>
      Manage Clients
    </button>

    <button onClick={() => navigate("/services")}>
  Create Service Types
</button>

<button onClick={() => navigate("/templates")}>
  Create Task Templates
</button>

    <button onClick={() => navigate("/tasks")}>
      View All Tasks
    </button>

    <button onClick={() => navigate("/engagements")}>
      View All Engagements
    </button>
  </div>
)}


        {/* MANAGER */}

        {role === "MANAGER" && (
          <div>

            <h2>
              Manager Controls
            </h2>

            <p>
              Manage engagements,
              assign tasks, review
              submitted work and
              approve or send work
              back.
            </p>

            <button
              onClick={() =>
                navigate("/engagements")
              }
            >
              Manage Engagements
            </button>

            <button
              onClick={() =>
                navigate("/tasks")
              }
            >
              Assign / Reassign Tasks
            </button>

            <button
              onClick={() =>
                navigate("/tasks")
              }
            >
              Review Submitted Work
            </button>

            <button
              onClick={() =>
                navigate("/tasks")
              }
            >
              Approve / Send Back
            </button>

          </div>
        )}


        {/* TEAM MEMBER */}

        {role === "TEAM_MEMBER" && (
          <div>

            <h2>
              Team Member Controls
            </h2>

            <p>
              View your own tasks,
              update task status and
              wait for client
              information.
            </p>

            <button
              onClick={() =>
                navigate("/tasks")
              }
            >
              My Tasks
            </button>

            <button
              onClick={() =>
                navigate("/tasks")
              }
            >
              Update Task Status
            </button>

            <button
              onClick={() =>
                navigate("/tasks")
              }
            >
              Waiting for Client
            </button>

          </div>
        )}

      </div>


      {/* =================================================
          TASK OVERVIEW
      ================================================= */}

      <h2>
        Task Overview
      </h2>

      <div className="dashboard-grid">

        <div className="dashboard-card">

          <h3>
            Total Tasks
          </h3>

          <strong>
            {summary.total_tasks}
          </strong>

        </div>


        <div className="dashboard-card">

          <h3>
            Open Tasks
          </h3>

          <strong>
            {summary.open_tasks}
          </strong>

        </div>


        <div className="dashboard-card">

          <h3>
            Overdue
          </h3>

          <strong>
            {summary.overdue_tasks}
          </strong>

        </div>


        <div className="dashboard-card">

          <h3>
            Due Today
          </h3>

          <strong>
            {summary.due_today}
          </strong>

        </div>


        <div className="dashboard-card">

          <h3>
            Waiting for Client
          </h3>

          <strong>
            {summary.waiting_for_client}
          </strong>

        </div>


        <div className="dashboard-card">

          <h3>
            Waiting for Review
          </h3>

          <strong>
            {summary.waiting_for_review}
          </strong>

        </div>


        <div className="dashboard-card">

          <h3>
            Completed
          </h3>

          <strong>
            {summary.completed_tasks}
          </strong>

        </div>

      </div>

    </div>
  );
}


/* =========================================================
   TASKS
========================================================= */

function Tasks() {
  const [tasks, setTasks] =
    useState([]);

  const [teamMembers, setTeamMembers] =
    useState([]);

  const [selectedStatuses, setSelectedStatuses] =
    useState({});

  const [selectedAssignees, setSelectedAssignees] =
    useState({});

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [message, setMessage] =
    useState("");

  const navigate =
    useNavigate();

  const role =
    localStorage.getItem("user_role");


  const loadTasks = async () => {

    try {

      const token =
        localStorage.getItem(
          "access_token"
        );

      if (!token) {
        navigate("/");
        return;
      }

      const headers = {
        Authorization:
          `Bearer ${token}`,
      };


      const response =
        await axios.get(
          "http://127.0.0.1:8001/tasks/",
          {
            headers,
          }
        );


      setTasks(
        response.data
      );


      const initialStatuses = {};
      const initialAssignees = {};

      response.data.forEach(
        (task) => {

          initialStatuses[task.id] =
            task.status;

          initialAssignees[task.id] =
            task.assigned_to_id || "";

        }
      );


      setSelectedStatuses(
        initialStatuses
      );

      setSelectedAssignees(
        initialAssignees
      );


    } catch (error) {

      console.error(
        "Task API error:",
        error
      );

      if (error.response) {

        if (
          error.response.status === 401
        ) {

          localStorage.removeItem(
            "access_token"
          );

          localStorage.removeItem(
            "user_role"
          );

          localStorage.removeItem(
            "user_name"
          );

          navigate("/");

          return;
        }

        setError(
          `Error ${error.response.status}: ${
            error.response.data.detail ||
            "Unable to load tasks"
          }`
        );

      } else {

        setError(
          "Unable to connect to backend"
        );
      }

    } finally {

      setLoading(false);
    }
  };


  const loadTeamMembers =
    async () => {

      try {

        const token =
          localStorage.getItem(
            "access_token"
          );

       const response =
  await axios.get(
    "http://127.0.0.1:8001/users/team-members",
    {
      headers: {
        Authorization:
          `Bearer ${token}`,
      },
    }
  );


        const members =
          response.data.filter(
            (user) =>
              user.role === "TEAM_MEMBER" &&
              user.is_active !== false
          );


        setTeamMembers(
          members
        );


      } catch (error) {

        console.error(
          "Unable to load team members:",
          error
        );
      }
    };


  useEffect(() => {

    const loadData =
      async () => {

        await loadTasks();

        if (
          role === "ADMIN" ||
          role === "MANAGER"
        ) {
          await loadTeamMembers();
        }

      };

    loadData();

  }, []);


  const handleStatusChange =
    (taskId, status) => {

      setSelectedStatuses(
        (previous) => ({
          ...previous,
          [taskId]: status,
        })
      );
    };


  const handleAssigneeChange =
    (taskId, userId) => {

      setSelectedAssignees(
        (previous) => ({
          ...previous,
          [taskId]: userId,
        })
      );
    };


  const updateStatus =
    async (taskId) => {

      try {

        setMessage("");

        const token =
          localStorage.getItem(
            "access_token"
          );

        const newStatus =
          selectedStatuses[taskId];


        await axios.put(
          `http://127.0.0.1:8001/tasks/${taskId}/status`,
          {
            status: newStatus,
          },
          {
            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );


        setMessage(
          "Task status updated successfully."
        );


        await loadTasks();


      } catch (error) {

        console.error(
          "Status update error:",
          error
        );

        if (error.response) {

          setMessage(
            error.response.data.detail ||
            "Unable to update task status."
          );

        } else {

          setMessage(
            "Unable to connect to backend."
          );
        }
      }
    };


  const assignTask =
    async (taskId) => {

      try {

        setMessage("");

        const token =
          localStorage.getItem(
            "access_token"
          );

        const assignedTo =
          selectedAssignees[taskId];


        if (!assignedTo) {

          setMessage(
            "Please select a team member."
          );

          return;
        }


        await axios.put(

          `http://127.0.0.1:8001/tasks/${taskId}/assign`,

          {
            assigned_to_id:
              Number(assignedTo),
          },

          {
            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }

        );


        setMessage(
          "Task assigned successfully."
        );


        await loadTasks();


      } catch (error) {

        console.error(
          "Task assignment error:",
          error
        );

        if (error.response) {

          setMessage(
            error.response.data.detail ||
            "Unable to assign task."
          );

        } else {

          setMessage(
            "Unable to connect to backend."
          );
        }
      }
    };


  const logout = () => {

    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "user_role"
    );

    localStorage.removeItem(
      "user_name"
    );

    navigate("/");
  };


  if (loading) {

    return (
      <div
        style={{
          padding: "40px"
        }}
      >

        <h1>
          Tasks
        </h1>

        <p>
          Loading tasks...
        </p>

      </div>
    );
  }


  if (error) {

    return (
      <div
        style={{
          padding: "40px"
        }}
      >

        <h1>
          Tasks
        </h1>

        <p>
          {error}
        </p>

        <button
          onClick={() =>
            navigate("/dashboard")
          }
        >
          Dashboard
        </button>

        <button
          onClick={logout}
          style={{
            marginLeft: "10px"
          }}
        >
          Logout
        </button>

      </div>
    );
  }


  return (
    <div
      style={{
        padding: "40px"
      }}
    >

      <h1>
        Tasks
      </h1>


      <div className="navigation-buttons">

        <button
          onClick={() =>
            navigate("/dashboard")
          }
        >
          Dashboard
        </button>

        <button
          onClick={() =>
            navigate("/tasks")
          }
        >
          Tasks
        </button>

        <button
          onClick={() =>
            navigate("/engagements")
          }
        >
          Engagements
        </button>

        <button
          onClick={() =>
            navigate("/clients")
          }
        >
          Clients
        </button>

        <button
          onClick={logout}
        >
          Logout
        </button>

      </div>


      {message && (
        <div className="task-message">
          {message}
        </div>
      )}


      <div className="tasks-container">

        {tasks.length === 0 ? (

          <p>
            No tasks found.
          </p>

        ) : (

          tasks.map((task) => (

            <div
              className="task-card"
              key={task.id}
            >

              <h3>
                {task.title}
              </h3>


              <p>
                <strong>
                  Task ID:
                </strong>{" "}
                {task.id}
              </p>


              <p>
                <strong>
                  Current Status:
                </strong>{" "}
                {task.status}
              </p>


              <p>
                <strong>
                  Due Date:
                </strong>{" "}
                {task.due_date ||
                  "Not assigned"}
              </p>

              {(role === "ADMIN" ||
  role === "MANAGER") && (

  <div
    style={{
      marginTop: "10px",
      marginBottom: "15px"
    }}
  >

    <label>
      Set Deadline:
    </label>

    <input
      type="date"
      value={
        task.due_date || ""
      }
      onChange={(e) => {

        setTasks((previousTasks) =>
          previousTasks.map((currentTask) =>
            currentTask.id === task.id
              ? {
                  ...currentTask,
                  due_date: e.target.value
                }
              : currentTask
          )
        );

      }}
      style={{
        display: "block",
        marginTop: "8px",
        marginBottom: "8px"
      }}
    />

    <button
      onClick={async () => {

        try {

          setMessage("");

          const token =
            localStorage.getItem(
              "access_token"
            );

          await axios.put(

            `http://127.0.0.1:8001/tasks/${task.id}/deadline`,

            {
              due_date:
                task.due_date
            },

            {
              headers: {
                Authorization:
                  `Bearer ${token}`,
              },
            }

          );

          setMessage(
            "Task deadline updated successfully."
          );

          await loadTasks();

        } catch (error) {

          if (error.response) {

            setMessage(
              error.response.data.detail ||
              "Unable to update task deadline."
            );

          } else {

            setMessage(
              "Unable to connect to backend."
            );
          }
        }

      }}
    >
      Update Deadline
    </button>

  </div>

)}


              <p>
                <strong>
                  Assigned To:
                </strong>{" "}
                {task.assigned_to_id ||
                  "Unassigned"}
              </p>


              {/* MANAGER / ADMIN ASSIGNMENT */}

              {(role === "ADMIN" ||
                role === "MANAGER") && (

                <div
                  style={{
                    marginTop: "15px",
                    marginBottom: "15px"
                  }}
                >

                  <label>
                    Assign / Reassign Task:
                  </label>


                  <select
                    value={
                      selectedAssignees[task.id] ||
                      ""
                    }
                    onChange={(e) =>
                      handleAssigneeChange(
                        task.id,
                        e.target.value
                      )
                    }
                    style={{
                      display: "block",
                      marginTop: "8px",
                      marginBottom: "10px"
                    }}
                  >

                    <option value="">
                      Select Team Member
                    </option>


                    {teamMembers.map(
                      (member) => (

                        <option
                          key={member.id}
                          value={member.id}
                        >
                          {member.name} - {member.email}
                        </option>

                      )
                    )}

                  </select>


                  <button
                    onClick={() =>
                      assignTask(task.id)
                    }
                  >
                    Assign Task
                  </button>

                </div>

              )}


              {/* STATUS UPDATE */}

              <label>
                Change Status:
              </label>


              <select
                value={
                  selectedStatuses[task.id] ||
                  task.status
                }
                onChange={(e) =>
                  handleStatusChange(
                    task.id,
                    e.target.value
                  )
                }
              >

                <option value="NOT_STARTED">
                  Not Started
                </option>

                <option value="IN_PROGRESS">
                  In Progress
                </option>

                <option value="WAITING_FOR_CLIENT">
                  Waiting for Client
                </option>

                <option value="READY_FOR_REVIEW">
                  Ready for Review
                </option>

                <option value="CHANGES_REQUESTED">
                  Changes Requested
                </option>

                <option value="COMPLETED">
                  Completed
                </option>

              </select>


              <button
                className="update-button"
                onClick={() =>
                  updateStatus(task.id)
                }
              >
                Update Status
              </button>
              {(role === "ADMIN" ||
  role === "MANAGER") &&
  task.status === "READY_FOR_REVIEW" && (

  <div
    style={{
      marginTop: "15px",
      display: "flex",
      gap: "10px",
      flexWrap: "wrap"
    }}
  >

    <button
      onClick={() => {

        setSelectedStatuses(
          (previous) => ({
            ...previous,
            [task.id]: "COMPLETED"
          })
        );

      }}
    >
      Approve
    </button>


    <button
      onClick={() => {

        setSelectedStatuses(
          (previous) => ({
            ...previous,
            [task.id]: "CHANGES_REQUESTED"
          })
        );

      }}
    >
      Send Back for Correction
    </button>

  </div>

)}

            </div>

          ))

        )}

      </div>

    </div>
  );
}


/* =========================================================
   ENGAGEMENTS
========================================================= */

function Engagements() {

  const [engagements, setEngagements] =
    useState([]);

  const [clients, setClients] =
    useState([]);

  const [services, setServices] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [message, setMessage] =
    useState("");

  const [editingEngagement, setEditingEngagement] =
  useState(null);

const [editName, setEditName] =
  useState("");

const [editStart, setEditStart] =
  useState("");

const [editEnd, setEditEnd] =
  useState("");

const [editDue, setEditDue] =
  useState("");

const [editStatus, setEditStatus] =
  useState("OPEN");

  const [form, setForm] =
    useState({
      client_id: "",
      service_type_id: "",
      name: "",
      period_start: "",
      period_end: "",
      due_date: "",
      status: "OPEN"
    });

  const navigate =
    useNavigate();

  const role =
    localStorage.getItem("user_role");


  /* LOGOUT */

  const logout = () => {

    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "user_role"
    );

    localStorage.removeItem(
      "user_name"
    );

    navigate("/");
  };


  /* LOAD DATA */

  useEffect(() => {

    const loadData =
      async () => {

        try {

          const token =
            localStorage.getItem(
              "access_token"
            );

          if (!token) {
            navigate("/");
            return;
          }

          const headers = {
            Authorization:
              `Bearer ${token}`,
          };


          const [
            engagementsResponse,
            clientsResponse,
            servicesResponse
          ] = await Promise.all([

            axios.get(
              "http://127.0.0.1:8001/engagements/",
              { headers }
            ),

            axios.get(
              "http://127.0.0.1:8001/clients/",
              { headers }
            ),

            axios.get(
              "http://127.0.0.1:8001/services/",
              { headers }
            )

          ]);


          setEngagements(
            engagementsResponse.data
          );

          setClients(
            clientsResponse.data
          );

          setServices(
            servicesResponse.data
          );


        } catch (error) {

          if (error.response) {

            if (
              error.response.status === 401
            ) {

              localStorage.removeItem(
                "access_token"
              );

              localStorage.removeItem(
                "user_role"
              );

              localStorage.removeItem(
                "user_name"
              );

              navigate("/");

              return;
            }

            setError(
              error.response.data.detail ||
              "Unable to load engagements"
            );

          } else {

            setError(
              "Unable to connect to backend"
            );
          }

        } finally {

          setLoading(false);
        }
      };


    loadData();

  }, [navigate]);


  /* FORM CHANGE */

  const handleChange = (e) => {

    setForm({
      ...form,
      [e.target.name]:
        e.target.value
    });

  };


  /* CREATE ENGAGEMENT */

  const createEngagement =
    async (e) => {

      e.preventDefault();

      setMessage("");
      setError("");

      try {

        const token =
          localStorage.getItem(
            "access_token"
          );


        const response =
          await axios.post(

            "http://127.0.0.1:8001/engagements/",

            {
              client_id:
                Number(form.client_id),

              service_type_id:
                Number(form.service_type_id),

              name:
                form.name,

              period_start:
                form.period_start,

              period_end:
                form.period_end,

              due_date:
                form.due_date,

              status:
                form.status
            },

            {
              headers: {
                Authorization:
                  `Bearer ${token}`,
              },
            }

          );


        setEngagements([
          ...engagements,
          response.data
        ]);


        setMessage(
          "Engagement created successfully. Tasks were generated automatically."
        );


        setForm({
          client_id: "",
          service_type_id: "",
          name: "",
          period_start: "",
          period_end: "",
          due_date: "",
          status: "OPEN"
        });


      } catch (error) {

        if (error.response) {

          setError(
            error.response.data.detail ||
            "Unable to create engagement"
          );

        } else {

          setError(
            "Unable to connect to backend"
          );
        }
      }
    };


  /* GENERATE NEXT RECURRING PERIOD */

  const generateNextPeriod =
    async (engagement) => {

      const token =
        localStorage.getItem(
          "access_token"
        );


      const confirmed =
        window.confirm(
          `Generate the next period for "${engagement.name}"?`
        );


      if (!confirmed) {
        return;
      }


      try {

        const response =
          await axios.post(

            `http://127.0.0.1:8001/engagements/${engagement.id}/generate-next`,

            {},

            {
              headers: {
                Authorization:
                  `Bearer ${token}`,
              },
            }

          );


        alert(
          response.data.message +
          `\n\nNew Engagement: ${response.data.name}`
        );


        const result =
          await axios.get(
            "http://127.0.0.1:8001/engagements/",
            {
              headers: {
                Authorization:
                  `Bearer ${token}`,
              },
            }
          );


        setEngagements(
          result.data
        );


      } catch (error) {

        console.error(error);

        alert(
          error.response?.data?.detail ||
          "Unable to generate next period."
        );
      }
    };

    const startEditEngagement = (engagement) => {
  setEditingEngagement(engagement);

  setEditName(engagement.name);
  setEditStart(engagement.period_start);
  setEditEnd(engagement.period_end);
  setEditDue(engagement.due_date);
  setEditStatus(engagement.status);

  setMessage("");
  setError("");

  window.scrollTo({
    top: 0,
    behavior: "smooth",
  });
};

const updateEngagement = async (e) => {
  e.preventDefault();

  const token =
    localStorage.getItem("access_token");

  try {

    const response = await axios.put(
      `http://127.0.0.1:8001/engagements/${editingEngagement.id}`,
      {
        name: editName,
        period_start: editStart,
        period_end: editEnd,
        due_date: editDue,
        status: editStatus,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    setMessage(
      "Engagement updated successfully."
    );

    setEngagements(
      engagements.map((engagement) =>
        engagement.id === editingEngagement.id
          ? response.data
          : engagement
      )
    );

    setEditingEngagement(null);

  } catch (error) {

    console.error(error);

    setError(
      error.response?.data?.detail ||
        "Unable to update engagement."
    );
  }
};



  /* LOADING */

  if (loading) {

    return (
      <div
        style={{
          padding: "40px"
        }}
      >

        <h1>
          Engagements
        </h1>

        <div className="navigation-buttons">

          <button
            onClick={() =>
              navigate("/dashboard")
            }
          >
            Dashboard
          </button>

          <button
            onClick={() =>
              navigate("/tasks")
            }
          >
            Tasks
          </button>

          <button
            onClick={() =>
              navigate("/engagements")
            }
          >
            Engagements
          </button>

          <button
            onClick={() =>
              navigate("/clients")
            }
          >
            Clients
          </button>

          <button
            onClick={logout}
          >
            Logout
          </button>

        </div>

        <p>
          Loading engagements...
        </p>

      </div>
    );
  }


  /* ERROR */

  if (
    error &&
    engagements.length === 0
  ) {

    return (
      <div
        style={{
          padding: "40px"
        }}
      >

        <h1>
          Engagements
        </h1>

        <div className="navigation-buttons">

          <button
            onClick={() =>
              navigate("/dashboard")
            }
          >
            Dashboard
          </button>

          <button
            onClick={() =>
              navigate("/tasks")
            }
          >
            Tasks
          </button>

          <button
            onClick={() =>
              navigate("/engagements")
            }
          >
            Engagements
          </button>

          <button
            onClick={() =>
              navigate("/clients")
            }
          >
            Clients
          </button>

          <button
            onClick={logout}
          >
            Logout
          </button>

        </div>

        <p>
          {error}
        </p>

      </div>
    );
  }


  /* MAIN PAGE */

  return (

    <div
      style={{
        padding: "40px"
      }}
    >

      <h1>
        Engagements
      </h1>


      {/* NAVIGATION */}

      <div className="navigation-buttons">

        <button
          onClick={() =>
            navigate("/dashboard")
          }
        >
          Dashboard
        </button>

        <button
          onClick={() =>
            navigate("/tasks")
          }
        >
          Tasks
        </button>

        <button
          onClick={() =>
            navigate("/engagements")
          }
        >
          Engagements
        </button>

        <button
          onClick={() =>
            navigate("/clients")
          }
        >
          Clients
        </button>

        <button
          onClick={logout}
        >
          Logout
        </button>

      </div>


      {/* CREATE ENGAGEMENT */}

      {(role === "ADMIN" ||
        role === "MANAGER") && (

        <div
          className="client-form"
          style={{
            marginBottom: "30px"
          }}
        >

          <h2>
            Create Engagement
          </h2>


          {message && (

            <p
              style={{
                color: "green",
                fontWeight: "600"
              }}
            >
              {message}
            </p>

          )}


          {error && (

            <p
              style={{
                color: "red",
                fontWeight: "600"
              }}
            >
              {error}
            </p>

          )}


          <form
            onSubmit={createEngagement}
          >

            {/* CLIENT */}

            <label>
              Client
            </label>

            <select
              name="client_id"
              value={form.client_id}
              onChange={handleChange}
              required
            >

              <option value="">
                Select Client
              </option>

              {clients.map(
                (client) => (

                  <option
                    key={client.id}
                    value={client.id}
                  >
                    {client.name}
                  </option>

                )
              )}

            </select>


            {/* SERVICE */}

            <label>
              Service Type
            </label>

            <select
              name="service_type_id"
              value={form.service_type_id}
              onChange={handleChange}
              required
            >

              <option value="">
                Select Service Type
              </option>

              {services.map(
                (service) => (

                  <option
                    key={service.id}
                    value={service.id}
                  >
                    {service.name}
                  </option>

                )
              )}

            </select>


            {/* NAME */}

            <label>
              Engagement Name
            </label>

            <input
              type="text"
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="e.g. ABC Consulting - October 2026 Accounting"
              required
            />


            {/* PERIOD START */}

            <label>
              Period Start
            </label>

            <input
              type="date"
              name="period_start"
              value={form.period_start}
              onChange={handleChange}
              required
            />


            {/* PERIOD END */}

            <label>
              Period End
            </label>

            <input
              type="date"
              name="period_end"
              value={form.period_end}
              onChange={handleChange}
              required
            />


            {/* DUE DATE */}

            <label>
              Due Date
            </label>

            <input
              type="date"
              name="due_date"
              value={form.due_date}
              onChange={handleChange}
              required
            />


            <button
              type="submit"
              style={{
                marginTop: "15px"
              }}
            >
              Create Engagement
            </button>

          </form>

        </div>

      )}

      {/* EDIT ENGAGEMENT */}

{editingEngagement && (

  <div
    className="client-form"
    style={{
      marginBottom: "30px"
    }}
  >

    <h2>
      Edit Engagement
    </h2>

    <form
      onSubmit={updateEngagement}
    >

      <label>
        Engagement Name
      </label>

      <input
        type="text"
        value={editName}
        onChange={(e) =>
          setEditName(e.target.value)
        }
        required
      />


      <label>
        Period Start
      </label>

      <input
        type="date"
        value={editStart}
        onChange={(e) =>
          setEditStart(e.target.value)
        }
        required
      />


      <label>
        Period End
      </label>

      <input
        type="date"
        value={editEnd}
        onChange={(e) =>
          setEditEnd(e.target.value)
        }
        required
      />


      <label>
        Due Date
      </label>

      <input
        type="date"
        value={editDue}
        onChange={(e) =>
          setEditDue(e.target.value)
        }
        required
      />


      <label>
        Status
      </label>

      <select
        value={editStatus}
        onChange={(e) =>
          setEditStatus(e.target.value)
        }
      >

        <option value="OPEN">
          OPEN
        </option>

        <option value="IN_PROGRESS">
          IN_PROGRESS
        </option>

        <option value="COMPLETED">
          COMPLETED
        </option>

        <option value="CLOSED">
          CLOSED
        </option>

      </select>


      <button
        type="submit"
        style={{
          marginTop: "15px"
        }}
      >
        Update Engagement
      </button>


      <button
        type="button"
        onClick={() =>
          setEditingEngagement(null)
        }
        style={{
          marginTop: "10px",
          marginLeft: "10px"
        }}
      >
        Cancel
      </button>

    </form>

  </div>

)}


      {/* ENGAGEMENT LIST */}

      <div className="engagements-container">

        {engagements.length === 0 ? (

          <p>
            No engagements found.
          </p>

        ) : (

          engagements.map(
            (engagement) => (

              <div
                className="engagement-card"
                key={engagement.id}
              >

                <h3>
                  {engagement.name}
                </h3>

                <p>
                  <strong>
                    Engagement ID:
                  </strong>{" "}
                  {engagement.id}
                </p>

                <p>
                  <strong>
                    Client ID:
                  </strong>{" "}
                  {engagement.client_id}
                </p>

                <p>
                  <strong>
                    Service Type ID:
                  </strong>{" "}
                  {engagement.service_type_id}
                </p>

                <p>
                  <strong>
                    Period:
                  </strong>{" "}
                  {engagement.period_start}
                  {" → "}
                  {engagement.period_end}
                </p>

                <p>
                  <strong>
                    Due Date:
                  </strong>{" "}
                  {engagement.due_date}
                </p>

                <p>
                  <strong>
                    Status:
                  </strong>{" "}
                  {engagement.status}
                </p>

                <button
  onClick={() =>
    startEditEngagement(engagement)
  }
  style={{
    marginTop: "10px",
    marginRight: "10px"
  }}
>
  Edit Engagement
</button>


                {/* GENERATE NEXT PERIOD */}

                {(role === "ADMIN" ||
                  role === "MANAGER") && (

                  <button
                    onClick={() =>
                      generateNextPeriod(
                        engagement
                      )
                    }
                    style={{
                      marginTop: "10px"
                    }}
                  >
                    Generate Next Period
                  </button>

                )}

              </div>

            )
          )

        )}

      </div>

    </div>
  );
}

/* =========================================================
   CLIENTS
========================================================= */

function Clients() {

  const [clients, setClients] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [showForm, setShowForm] =
    useState(false);

  const [clientName, setClientName] =
    useState("");

  const [clientEmail, setClientEmail] =
    useState("");

  const [clientPhone, setClientPhone] =
    useState("");

  const [clientMessage, setClientMessage] =
    useState("");

  const [editingClient, setEditingClient] =
    useState(null);

  const [editName, setEditName] =
    useState("");

  const [editEmail, setEditEmail] =
    useState("");

  const [editPhone, setEditPhone] =
    useState("");

  const navigate =
    useNavigate();


  const logout = () => {

    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "user_role"
    );

    localStorage.removeItem(
      "user_name"
    );

    navigate("/");
  };


  /* CREATE CLIENT */

  const createClient =
    async (e) => {

      e.preventDefault();

      try {

        const token =
          localStorage.getItem(
            "access_token"
          );

        await axios.post(
          "http://127.0.0.1:8001/clients/",
          {
            name: clientName,
            email: clientEmail,
            phone: clientPhone,
          },
          {
            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );

        setClientMessage(
          "Client created successfully."
        );

        setClientName("");
        setClientEmail("");
        setClientPhone("");

        setShowForm(false);


        const response =
          await axios.get(
            "http://127.0.0.1:8001/clients/",
            {
              headers: {
                Authorization:
                  `Bearer ${token}`,
              },
            }
          );

        setClients(
          response.data
        );

      } catch (error) {

        if (error.response) {

          setClientMessage(
            error.response.data.detail ||
            "Unable to create client."
          );

        } else {

          setClientMessage(
            "Unable to connect to backend."
          );
        }
      }
    };


  /* START EDIT */

  const startEditClient =
    (client) => {

      setEditingClient(client);

      setEditName(
        client.name
      );

      setEditEmail(
        client.email
      );

      setEditPhone(
        client.phone || ""
      );

      setClientMessage("");
    };

    /* DEACTIVATE CLIENT */

const handleDeactivate = async (client) => {
  const confirmed = window.confirm(
    `Are you sure you want to deactivate ${client.name}?`
  );

  if (!confirmed) {
    return;
  }

  try {
    const token =
      localStorage.getItem("access_token");

    await axios.delete(
      `http://127.0.0.1:8001/clients/${client.id}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    setClientMessage(
      "Client deactivated successfully."
    );

    const response = await axios.get(
      "http://127.0.0.1:8001/clients/",
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    setClients(response.data);

  } catch (error) {
    console.error(error);

    if (error.response) {
      setClientMessage(
        error.response.data.detail ||
          "Unable to deactivate client."
      );
    } else {
      setClientMessage(
        "Unable to connect to backend."
      );
    }
  }
};


  /* UPDATE CLIENT */

  const updateClient =
    async (e) => {

      e.preventDefault();

      try {

        const token =
          localStorage.getItem(
            "access_token"
          );

        await axios.put(
          `http://127.0.0.1:8001/clients/${editingClient.id}`,
          {
            name: editName,
            email: editEmail,
            phone: editPhone,
          },
          {
            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );

        setClientMessage(
          "Client updated successfully."
        );

        setEditingClient(null);


        const response =
          await axios.get(
            "http://127.0.0.1:8001/clients/",
            {
              headers: {
                Authorization:
                  `Bearer ${token}`,
              },
            }
          );

        setClients(
          response.data
        );

      } catch (error) {

        if (error.response) {

          setClientMessage(
            error.response.data.detail ||
            "Unable to update client."
          );

        } else {

          setClientMessage(
            "Unable to connect to backend."
          );
        }
      }
    };


  /* LOAD CLIENTS */

  useEffect(() => {

    const loadClients =
      async () => {

        try {

          const token =
            localStorage.getItem(
              "access_token"
            );

          if (!token) {
            navigate("/");
            return;
          }

          const response =
            await axios.get(
              "http://127.0.0.1:8001/clients/",
              {
                headers: {
                  Authorization:
                    `Bearer ${token}`,
                },
              }
            );

          setClients(
            response.data
          );

        } catch (error) {

          if (error.response) {

            setError(
              error.response.data.detail ||
              "Unable to load clients"
            );

          } else {

            setError(
              "Unable to connect to backend"
            );
          }

        } finally {

          setLoading(false);
        }
      };


    loadClients();

  }, []);


  /* LOADING */

  if (loading) {

    return (
      <div
        style={{
          padding: "40px"
        }}
      >

        <h1>
          Clients
        </h1>

        <div className="navigation-buttons">

          <button
            onClick={() =>
              navigate("/dashboard")
            }
          >
            Dashboard
          </button>

          <button
            onClick={() =>
              navigate("/tasks")
            }
          >
            Tasks
          </button>

          <button
            onClick={() =>
              navigate("/engagements")
            }
          >
            Engagements
          </button>

          <button
            onClick={() =>
              navigate("/clients")
            }
          >
            Clients
          </button>

          <button
            onClick={logout}
          >
            Logout
          </button>

        </div>

        <p>
          Loading clients...
        </p>

      </div>
    );
  }


  /* ERROR */

  if (error) {

    return (
      <div
        style={{
          padding: "40px"
        }}
      >

        <h1>
          Clients
        </h1>

        <div className="navigation-buttons">

          <button
            onClick={() =>
              navigate("/dashboard")
            }
          >
            Dashboard
          </button>

          <button
            onClick={() =>
              navigate("/tasks")
            }
          >
            Tasks
          </button>

          <button
            onClick={() =>
              navigate("/engagements")
            }
          >
            Engagements
          </button>

          <button
            onClick={() =>
              navigate("/clients")
            }
          >
            Clients
          </button>

          <button
            onClick={logout}
          >
            Logout
          </button>

        </div>

        <p>
          {error}
        </p>

      </div>
    );
  }


  /* MAIN CLIENT PAGE */

  return (
    <div
      style={{
        padding: "40px"
      }}
    >

      <h1>
        Clients
      </h1>


      {/* NAVIGATION */}

      <div className="navigation-buttons">

        <button
          onClick={() =>
            navigate("/dashboard")
          }
        >
          Dashboard
        </button>

        <button
          onClick={() =>
            navigate("/tasks")
          }
        >
          Tasks
        </button>

        <button
          onClick={() =>
            navigate("/engagements")
          }
        >
          Engagements
        </button>

        <button
  onClick={() =>
    navigate("/services")
  }
>
  Services
</button>

        <button
          onClick={() =>
            navigate("/services")
          }
        >
          Services
        </button>

<button
  onClick={() =>
    navigate("/clients")
  }
></button>

        <button
          onClick={() =>
            navigate("/clients")
          }
        >
          Clients
        </button>

        <button
          onClick={logout}
        >
          Logout
        </button>

      </div>


      {/* CREATE CLIENT BUTTON */}

      <button
        onClick={() => {

          setShowForm(
            !showForm
          );

          setClientMessage("");
        }}
      >
        {showForm
          ? "Cancel"
          : "Create Client"}
      </button>


      {/* CREATE CLIENT FORM */}

      {showForm && (

        <form
          className="client-form"
          onSubmit={createClient}
        >

          <h2>
            Create New Client
          </h2>

          <label>
            Client Name
          </label>

          <input
            type="text"
            value={clientName}
            onChange={(e) =>
              setClientName(
                e.target.value
              )
            }
            placeholder="Enter client name"
            required
          />


          <label>
            Email
          </label>

          <input
            type="email"
            value={clientEmail}
            onChange={(e) =>
              setClientEmail(
                e.target.value
              )
            }
            placeholder="Enter email"
            required
          />


          <label>
            Phone
          </label>

          <input
            type="text"
            value={clientPhone}
            onChange={(e) =>
              setClientPhone(
                e.target.value
              )
            }
            placeholder="Enter phone number"
          />


          <button type="submit">
            Create Client
          </button>

        </form>
      )}


      {/* EDIT CLIENT FORM */}

      {editingClient && (

        <form
          className="client-form"
          onSubmit={updateClient}
        >

          <h2>
            Edit Client
          </h2>

          <label>
            Client Name
          </label>

          <input
            type="text"
            value={editName}
            onChange={(e) =>
              setEditName(
                e.target.value
              )
            }
            required
          />


          <label>
            Email
          </label>

          <input
            type="email"
            value={editEmail}
            onChange={(e) =>
              setEditEmail(
                e.target.value
              )
            }
            required
          />


          <label>
            Phone
          </label>

          <input
            type="text"
            value={editPhone}
            onChange={(e) =>
              setEditPhone(
                e.target.value
              )
            }
          />


          <button type="submit">
            Update Client
          </button>

          <button
            type="button"
            onClick={() =>
              setEditingClient(null)
            }
          >
            Cancel
          </button>

        </form>
      )}


      {/* MESSAGE */}

      {clientMessage && (

        <div className="task-message">
          {clientMessage}
        </div>

      )}


      {/* CLIENT LIST */}

      <div className="clients-container">

        {clients.length === 0 ? (

          <p>
            No clients found.
          </p>

        ) : (

          clients.map(
            (client) => (

              <div
                className="client-card"
                key={client.id}
              >

                <h3>
                  {client.name}
                </h3>

                <p>
                  <strong>
                    Client ID:
                  </strong>{" "}
                  {client.id}
                </p>

                <p>
                  <strong>
                    Email:
                  </strong>{" "}
                  {client.email}
                </p>

                <p>
                  <strong>
                    Phone:
                  </strong>{" "}
                  {client.phone ||
                    "Not provided"}
                </p>

                <p>
                  <strong>
                    Status:
                  </strong>{" "}

                  {client.is_active
                    ? "Active"
                    : "Inactive"}
                </p>


                {/* EDIT */}

                <button
                  onClick={() =>
                    startEditClient(client)
                  }
                >
                  Edit Client
                </button>


                {/* DEACTIVATE - CURRENTLY TEST BUTTON */}

                <button
  onClick={() => handleDeactivate(client)}
>
  Deactivate
</button>

              </div>

            )
          )

        )}

      </div>

    </div>
  );
}

function Users() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("TEAM_MEMBER");

  const [message, setMessage] = useState("");

  const navigate = useNavigate();

  const token =
    localStorage.getItem("access_token");

  const axiosConfig = {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };


  // =========================
  // LOAD USERS
  // =========================

  const loadUsers = async () => {

    try {

      setLoading(true);

      const response =
        await axios.get(
          "http://127.0.0.1:8001/users/",
          axiosConfig
        );

      setUsers(response.data);

    } catch (error) {

      if (error.response) {

        setMessage(
          error.response.data.detail ||
          "Unable to load users"
        );

      } else {

        setMessage(
          "Unable to connect to backend"
        );
      }

    } finally {

      setLoading(false);
    }
  };


  useEffect(() => {

    loadUsers();

  }, []);


  // =========================
  // OPEN CREATE FORM
  // =========================

  const openCreateForm = () => {

    setEditingUser(null);

    setName("");
    setEmail("");
    setPassword("");
    setRole("TEAM_MEMBER");

    setMessage("");

    setShowForm(true);
  };


  // =========================
  // OPEN EDIT FORM
  // =========================

  const openEditForm = (user) => {

    setEditingUser(user);

    setName(user.name);
    setEmail(user.email);
    setPassword("");
    setRole(user.role);

    setMessage("");

    setShowForm(true);
  };


  // =========================
  // CLOSE FORM
  // =========================

  const closeForm = () => {

    setShowForm(false);
    setEditingUser(null);

    setName("");
    setEmail("");
    setPassword("");
    setRole("TEAM_MEMBER");

    setMessage("");
  };


  // =========================
  // CREATE USER
  // =========================

  const createUser = async (e) => {

    e.preventDefault();

    try {

      await axios.post(
        "http://127.0.0.1:8001/users/",
        {
          name: name,
          email: email,
          password: password,
          role: role,
        },
        axiosConfig
      );

      setMessage(
        "User created successfully"
      );

      closeForm();

      await loadUsers();

    } catch (error) {

      if (error.response) {

        setMessage(
          error.response.data.detail ||
          "Unable to create user"
        );

      } else {

        setMessage(
          "Unable to connect to backend"
        );
      }
    }
  };


  // =========================
  // UPDATE USER
  // =========================

  const updateUser = async (e) => {

    e.preventDefault();

    if (!editingUser) {
      return;
    }

    try {

      const updateData = {
        name: name,
        email: email,
        role: role,
      };


      // Only send password if entered
      if (password.trim() !== "") {

        updateData.password =
          password;
      }


      await axios.put(
        `http://127.0.0.1:8001/users/${editingUser.id}`,
        updateData,
        axiosConfig
      );


      setMessage(
        "User updated successfully"
      );

      closeForm();

      await loadUsers();

    } catch (error) {

      if (error.response) {

        setMessage(
          error.response.data.detail ||
          "Unable to update user"
        );

      } else {

        setMessage(
          "Unable to connect to backend"
        );
      }
    }
  };


  // =========================
  // DEACTIVATE USER
  // =========================

  const deactivateUser = async (user) => {

    if (
      !window.confirm(
        `Are you sure you want to deactivate ${user.name}?`
      )
    ) {
      return;
    }


    try {

      await axios.delete(
        `http://127.0.0.1:8001/users/${user.id}`,
        axiosConfig
      );


      setMessage(
        "User deactivated successfully"
      );

      await loadUsers();

    } catch (error) {

      if (error.response) {

        setMessage(
          error.response.data.detail ||
          "Unable to deactivate user"
        );

      } else {

        setMessage(
          "Unable to connect to backend"
        );
      }
    }
  };


  // =========================
  // ACTIVATE USER
  // =========================

  const activateUser = async (user) => {

    try {

      await axios.put(
        `http://127.0.0.1:8001/users/${user.id}/activate`,
        {},
        axiosConfig
      );


      setMessage(
        "User activated successfully"
      );

      await loadUsers();

    } catch (error) {

      if (error.response) {

        setMessage(
          error.response.data.detail ||
          "Unable to activate user"
        );

      } else {

        setMessage(
          "Unable to connect to backend"
        );
      }
    }
  };


  // =========================
  // LOGOUT
  // =========================

  const logout = () => {

    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "user_role"
    );

    localStorage.removeItem(
      "user_name"
    );

    navigate("/");
  };


  return (
    <div className="page-container">

      <h1>
        Manage Users
      </h1>

      <p>
        Create and manage system users
        and their roles.
      </p>


      {/* NAVIGATION */}

      <div className="navigation-buttons">

        <button
          onClick={() =>
            navigate("/dashboard")
          }
        >
          Dashboard
        </button>

        <button
          onClick={() =>
            navigate("/tasks")
          }
        >
          Tasks
        </button>

        <button
          onClick={() =>
            navigate("/engagements")
          }
        >
          Engagements
        </button>

        <button
          onClick={() =>
            navigate("/clients")
          }
        >
          Clients
        </button>

        <button
          onClick={logout}
        >
          Logout
        </button>

      </div>


      {/* CREATE USER BUTTON */}

      <button
        onClick={() => {

          if (showForm) {
            closeForm();
          } else {
            openCreateForm();
          }

        }}
      >
        {showForm
          ? "Close Form"
          : "Create User"}
      </button>


      {/* USER FORM */}

      {showForm && (

        <form
          className="client-form"
          onSubmit={
            editingUser
              ? updateUser
              : createUser
          }
        >

          <h2>
            {editingUser
              ? "Edit User"
              : "Create New User"}
          </h2>


          {/* NAME */}

          <label>
            Name
          </label>

          <input
            type="text"
            placeholder="Enter user name"
            value={name}
            onChange={(e) =>
              setName(e.target.value)
            }
            required
          />


          {/* EMAIL */}

          <label>
            Email
          </label>

          <input
            type="email"
            placeholder="Enter email"
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
            required
          />


          {/* PASSWORD */}

          <label>
            Password
            {editingUser &&
              " (leave blank to keep current password)"}
          </label>

          <input
            type="password"
            placeholder={
              editingUser
                ? "Enter new password only if changing it"
                : "Enter password"
            }
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
            required={!editingUser}
          />


          {/* ROLE */}

          <label>
            Role
          </label>

          <select
            value={role}
            onChange={(e) =>
              setRole(e.target.value)
            }
          >

            <option value="ADMIN">
              Admin
            </option>

            <option value="MANAGER">
              Manager
            </option>

            <option value="TEAM_MEMBER">
              Team Member
            </option>

          </select>


          <button type="submit">

            {editingUser
              ? "Update User"
              : "Create User"}

          </button>


          {editingUser && (

            <button
              type="button"
              onClick={closeForm}
              style={{
                marginLeft: "10px"
              }}
            >
              Cancel
            </button>

          )}

        </form>
      )}


      {/* MESSAGE */}

      {message && (

        <div className="task-message">
          {message}
        </div>

      )}


      {/* USERS */}

      {loading ? (

        <p>
          Loading users...
        </p>

      ) : users.length === 0 ? (

        <p>
          No users found.
        </p>

      ) : (

        <div className="clients-container">

          {users.map((user) => (

            <div
              className="client-card"
              key={user.id}
            >

              <h3>
                {user.name}
              </h3>


              <p>
                <strong>
                  Email:
                </strong>{" "}
                {user.email}
              </p>


              <p>
                <strong>
                  Role:
                </strong>{" "}
                {user.role}
              </p>


              <p>
                <strong>
                  Status:
                </strong>{" "}
                {user.is_active
                  ? "Active"
                  : "Inactive"}
              </p>


              {/* EDIT */}

              <button
                onClick={() =>
                  openEditForm(user)
                }
              >
                Edit User
              </button>


              {/* ACTIVATE / DEACTIVATE */}

              {user.is_active ? (

                <button
                  onClick={() =>
                    deactivateUser(user)
                  }
                  style={{
                    marginLeft: "10px"
                  }}
                >
                  Deactivate User
                </button>

              ) : (

                <button
                  onClick={() =>
                    activateUser(user)
                  }
                  style={{
                    marginLeft: "10px"
                  }}
                >
                  Activate User
                </button>

              )}

            </div>

          ))}

        </div>

      )}

    </div>
  );
}

function Services() {
  const [services, setServices] = useState([]);
  const [form, setForm] = useState({
    name: "",
    description: "",
    engagement_type: "ONE_TIME",
  });

  const [editingId, setEditingId] = useState(null);
  const [message, setMessage] = useState("");

  const token = localStorage.getItem("access_token");

  const loadServices = async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8001/services/",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setServices(response.data);
    } catch (error) {
      console.error(error);
      setMessage("Unable to load services.");
    }
  };

  useEffect(() => {
    loadServices();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    try {
      if (editingId) {
        await axios.put(
          `http://127.0.0.1:8001/services/${editingId}`,
          {
            name: form.name,
            description: form.description,
            engagement_type: form.engagement_type,
          },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        setMessage("Service updated successfully.");
      } else {
        await axios.post(
          "http://127.0.0.1:8001/services/",
          {
            name: form.name,
            description: form.description,
            engagement_type: form.engagement_type,
          },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        setMessage("Service created successfully.");
      }

      setForm({
        name: "",
        description: "",
        engagement_type: "ONE_TIME",
      });

      setEditingId(null);
      loadServices();
    } catch (error) {
      console.error(error);

      setMessage(
        error.response?.data?.detail ||
          "Unable to save service."
      );
    }
  };

  const handleEdit = (service) => {
    setEditingId(service.id);

    setForm({
      name: service.name || "",
      description: service.description || "",
      engagement_type:
        service.engagement_type || "ONE_TIME",
    });

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const handleCancelEdit = () => {
    setEditingId(null);

    setForm({
      name: "",
      description: "",
      engagement_type: "ONE_TIME",
    });

    setMessage("");
  };

  const handleDeactivate = async (id) => {
    const confirmed = window.confirm(
      "Are you sure you want to deactivate this service?"
    );

    if (!confirmed) {
      return;
    }

    try {
      await axios.delete(
        `http://127.0.0.1:8001/services/${id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setMessage("Service deactivated successfully.");
      loadServices();
    } catch (error) {
      console.error(error);

      setMessage(
        error.response?.data?.detail ||
          "Unable to deactivate service."
      );
    }
  };

  const handleActivate = async (service) => {
    try {
      await axios.put(
        `http://127.0.0.1:8001/services/${service.id}`,
        {
          name: service.name,
          description: service.description || "",
          engagement_type: service.engagement_type,
          is_active: true,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setMessage("Service activated successfully.");
      loadServices();
    } catch (error) {
      console.error(error);

      setMessage(
        error.response?.data?.detail ||
          "Unable to activate service."
      );
    }
  };

  return (
    <div className="page-container">

      <div className="page-header">
        <div>
          <h1>Service Types</h1>
          <p>
            Create and manage professional service types.
          </p>
        </div>

        <div className="page-actions">
          <button onClick={() => window.location.href = "/dashboard"}>
            Dashboard
          </button>

          <button onClick={() => window.location.href = "/tasks"}>
            Tasks
          </button>

          <button onClick={() => window.location.href = "/engagements"}>
            Engagements
          </button>

          <button onClick={() => window.location.href = "/clients"}>
            Clients
          </button>

          <button
            onClick={() => {
              localStorage.clear();
              window.location.href = "/";
            }}
          >
            Logout
          </button>
        </div>
      </div>

      <div className="form-card">

        <h2>
          {editingId
            ? "Edit Service Type"
            : "Create Service Type"}
        </h2>

        <form onSubmit={handleSubmit}>

          <div className="form-group">
            <label>Service Name</label>

            <input
              type="text"
              value={form.name}
              onChange={(e) =>
                setForm({
                  ...form,
                  name: e.target.value,
                })
              }
              placeholder="Example: Monthly Accounting"
              required
            />
          </div>

          <div className="form-group">
            <label>Description</label>

            <textarea
              value={form.description}
              onChange={(e) =>
                setForm({
                  ...form,
                  description: e.target.value,
                })
              }
              placeholder="Enter service description"
              rows="4"
            />
          </div>

          <div className="form-group">
            <label>Engagement Type</label>

            <select
              value={form.engagement_type}
              onChange={(e) =>
                setForm({
                  ...form,
                  engagement_type: e.target.value,
                })
              }
            >
              <option value="ONE_TIME">
                One Time
              </option>

              <option value="RECURRING">
                Recurring
              </option>
            </select>
          </div>

          <div className="form-buttons">

            <button type="submit">
              {editingId
                ? "Update Service"
                : "Create Service"}
            </button>

            {editingId && (
              <button
                type="button"
                onClick={handleCancelEdit}
              >
                Cancel
              </button>
            )}

          </div>

        </form>

        {message && (
          <p className="message">
            {message}
          </p>
        )}

      </div>

      <div className="list-card">

        <h2>All Service Types</h2>

        {services.length === 0 ? (
          <p>No service types found.</p>
        ) : (
          <div className="table-container">

            <table>

              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Description</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>

                {services.map((service) => (

                  <tr key={service.id}>

                    <td>{service.id}</td>

                    <td>{service.name}</td>

                    <td>
                      {service.description || "-"}
                    </td>

                    <td>
                      {service.engagement_type}
                    </td>

                    <td>
                      {service.is_active ? (
                        <span className="status-active">
                          Active
                        </span>
                      ) : (
                        <span className="status-inactive">
                          Inactive
                        </span>
                      )}
                    </td>

                    <td>

                      <button
                        onClick={() =>
                          handleEdit(service)
                        }
                      >
                        Edit
                      </button>

                      {service.is_active ? (
                        <button
                          onClick={() =>
                            handleDeactivate(service.id)
                          }
                        >
                          Deactivate
                        </button>
                      ) : (
                        <button
                          onClick={() =>
                            handleActivate(service)
                          }
                        >
                          Activate
                        </button>
                      )}

                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>
        )}

      </div>

    </div>
  );
}


function Templates() {
  const [templates, setTemplates] = useState([]);
  const [services, setServices] = useState([]);

  const [form, setForm] = useState({
    service_type_id: "",
    name: "",
    description: "",
    default_days: 1,
    sequence: 1,
  });

  const [editingId, setEditingId] = useState(null);
  const [message, setMessage] = useState("");

  const token = localStorage.getItem("access_token");

  const headers = {
    Authorization: `Bearer ${token}`,
  };

  const loadTemplates = async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8001/templates/",
        {
          headers,
        }
      );

      setTemplates(response.data);
    } catch (error) {
      console.error(error);
      setMessage("Unable to load task templates.");
    }
  };

  const loadServices = async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8001/services/",
        {
          headers,
        }
      );

      setServices(response.data);
    } catch (error) {
      console.error(error);
      setMessage("Unable to load services.");
    }
  };

  useEffect(() => {
    loadTemplates();
    loadServices();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    const data = {
      service_type_id: Number(form.service_type_id),
      name: form.name,
      description: form.description,
      default_days: Number(form.default_days),
      sequence: Number(form.sequence),
    };

    try {
      if (editingId) {
        await axios.put(
          `http://127.0.0.1:8001/templates/${editingId}`,
          data,
          {
            headers,
          }
        );

        setMessage("Task template updated successfully.");
      } else {
        await axios.post(
          "http://127.0.0.1:8001/templates/",
          data,
          {
            headers,
          }
        );

        setMessage("Task template created successfully.");
      }

      resetForm();
      loadTemplates();
    } catch (error) {
      console.error(error);

      setMessage(
        error.response?.data?.detail ||
          "Unable to save task template."
      );
    }
  };

  const resetForm = () => {
    setEditingId(null);

    setForm({
      service_type_id: "",
      name: "",
      description: "",
      default_days: 1,
      sequence: 1,
    });
  };

  const handleEdit = (template) => {
    setEditingId(template.id);

    setForm({
      service_type_id: template.service_type_id,
      name: template.name || "",
      description: template.description || "",
      default_days: template.default_days || 1,
      sequence: template.sequence || 1,
    });

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const handleDelete = async (id) => {
    const confirmed = window.confirm(
      "Are you sure you want to deactivate this task template?"
    );

    if (!confirmed) {
      return;
    }

    try {
      await axios.delete(
        `http://127.0.0.1:8001/templates/${id}`,
        {
          headers,
        }
      );

      setMessage("Task template deactivated successfully.");
      loadTemplates();
    } catch (error) {
      console.error(error);

      setMessage(
        error.response?.data?.detail ||
          "Unable to deactivate task template."
      );
    }
  };

  const handleActivate = async (template) => {
    try {
      await axios.put(
        `http://127.0.0.1:8001/templates/${template.id}`,
        {
          service_type_id: template.service_type_id,
          name: template.name,
          description: template.description || "",
          default_days: template.default_days,
          sequence: template.sequence,
          is_active: true,
        },
        {
          headers,
        }
      );

      setMessage("Task template activated successfully.");
      loadTemplates();
    } catch (error) {
      console.error(error);

      setMessage(
        error.response?.data?.detail ||
          "Unable to activate task template."
      );
    }
  };

  const getServiceName = (serviceId) => {
    const service = services.find(
      (item) => item.id === serviceId
    );

    return service ? service.name : `Service #${serviceId}`;
  };

  return (
    <div className="page-container">

      <div className="page-header">

        <div>
          <h1>Task Templates</h1>

          <p>
            Create and manage tasks generated for each service.
          </p>
        </div>

        <div className="page-actions">

          <button
            onClick={() =>
              (window.location.href = "/dashboard")
            }
          >
            Dashboard
          </button>

          <button
            onClick={() =>
              (window.location.href = "/tasks")
            }
          >
            Tasks
          </button>

          <button
            onClick={() =>
              (window.location.href = "/engagements")
            }
          >
            Engagements
          </button>

          <button
            onClick={() =>
              (window.location.href = "/clients")
            }
          >
            Clients
          </button>

          <button
            onClick={() => {
              localStorage.clear();
              window.location.href = "/";
            }}
          >
            Logout
          </button>

        </div>
      </div>

      <div className="form-card">

        <h2>
          {editingId
            ? "Edit Task Template"
            : "Create Task Template"}
        </h2>

        <form onSubmit={handleSubmit}>

          <div className="form-group">

            <label>Service Type</label>

            <select
              value={form.service_type_id}
              onChange={(e) =>
                setForm({
                  ...form,
                  service_type_id: e.target.value,
                })
              }
              required
            >

              <option value="">
                Select Service Type
              </option>

              {services
                .filter((service) => service.is_active)
                .map((service) => (
                  <option
                    key={service.id}
                    value={service.id}
                  >
                    {service.name}
                  </option>
                ))}

            </select>

          </div>

          <div className="form-group">

            <label>Task Name</label>

            <input
              type="text"
              value={form.name}
              onChange={(e) =>
                setForm({
                  ...form,
                  name: e.target.value,
                })
              }
              placeholder="Example: Collect financial documents"
              required
            />

          </div>

          <div className="form-group">

            <label>Description</label>

            <textarea
              value={form.description}
              onChange={(e) =>
                setForm({
                  ...form,
                  description: e.target.value,
                })
              }
              placeholder="Describe the task"
              rows="3"
            />

          </div>

          <div className="form-group">

            <label>Default Days</label>

            <input
              type="number"
              min="0"
              value={form.default_days}
              onChange={(e) =>
                setForm({
                  ...form,
                  default_days: e.target.value,
                })
              }
              required
            />

          </div>

          <div className="form-group">

            <label>Sequence</label>

            <input
              type="number"
              min="1"
              value={form.sequence}
              onChange={(e) =>
                setForm({
                  ...form,
                  sequence: e.target.value,
                })
              }
              required
            />

          </div>

          <div className="form-buttons">

            <button type="submit">
              {editingId
                ? "Update Template"
                : "Create Template"}
            </button>

            {editingId && (
              <button
                type="button"
                onClick={resetForm}
              >
                Cancel
              </button>
            )}

          </div>

        </form>

        {message && (
          <p className="message">
            {message}
          </p>
        )}

      </div>

      <div className="list-card">

        <h2>All Task Templates</h2>

        {templates.length === 0 ? (
          <p>No task templates found.</p>
        ) : (

          <div className="table-container">

            <table>

              <thead>

                <tr>
                  <th>ID</th>
                  <th>Service</th>
                  <th>Task Name</th>
                  <th>Description</th>
                  <th>Default Days</th>
                  <th>Sequence</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>

              </thead>

              <tbody>

                {templates.map((template) => (

                  <tr key={template.id}>

                    <td>{template.id}</td>

                    <td>
                      {getServiceName(
                        template.service_type_id
                      )}
                    </td>

                    <td>{template.name}</td>

                    <td>
                      {template.description || "-"}
                    </td>

                    <td>
                      {template.default_days}
                    </td>

                    <td>
                      {template.sequence}
                    </td>

                    <td>

                      {template.is_active ? (
                        <span className="status-active">
                          Active
                        </span>
                      ) : (
                        <span className="status-inactive">
                          Inactive
                        </span>
                      )}

                    </td>

                    <td>

                      <button
                        onClick={() =>
                          handleEdit(template)
                        }
                      >
                        Edit
                      </button>

                      {template.is_active ? (

                        <button
                          onClick={() =>
                            handleDelete(template.id)
                          }
                        >
                          Deactivate
                        </button>

                      ) : (

                        <button
                          onClick={() =>
                            handleActivate(template)
                          }
                        >
                          Activate
                        </button>

                      )}

                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

        )}

      </div>

    </div>
  );
}


function App() {

  return (
    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={<Login />}
        />

        <Route
          path="/dashboard"
          element={<Dashboard />}
        />

        <Route
  path="/users"
  element={<Users />}
/>

<Route
  path="/services"
  element={<Services />}
/>

<Route
  path="/templates"
  element={<Templates />}
/>

        <Route
          path="/tasks"
          element={<Tasks />}
        />

        <Route
          path="/engagements"
          element={<Engagements />}
        />

        <Route
          path="/clients"
          element={<Clients />}
        />

        <Route
  path="/services"
  element={<Services />}
/>

      </Routes>

    </BrowserRouter>
  );
}


export default App;