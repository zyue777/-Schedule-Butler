module.exports = {
  apps: [{
    name: "calendar-bot",
    script: "./main.py",
    interpreter: "./venv/bin/python3",
    watch: false,
    env: {
      NODE_ENV: "production"
    },
    error_file: "logs/error.log",
    out_file: "logs/out.log",
    time: true
  }]
}
