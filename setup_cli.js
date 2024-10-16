const readline = require('readline');
const { exec } = require('child_process');
const fs = require('fs');

// Create readline interface
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Helper function to print slowly
function printSlowly(text, delay = 30) {
  return new Promise((resolve) => {
    let i = 0;
    const interval = setInterval(() => {
      process.stdout.write(text[i]);
      i++;
      if (i === text.length) {
        clearInterval(interval);
        console.log();
        resolve();
      }
    }, delay);
  });
}

// Helper function to get input
function getInput(prompt) {
  return new Promise((resolve) => {
    rl.question(prompt, (answer) => {
      resolve(answer);
    });
  });
}

// Helper function to run shell commands
function runCommand(command) {
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error: ${error.message}`);
        reject(error);
      }
      if (stderr) {
        console.error(`stderr: ${stderr}`);
      }
      console.log(stdout);
      resolve(stdout);
    });
  });
}

// Setup Vercel with GitHub
async function setupVercel() {
  await printSlowly("Setting up Vercel...");
  await printSlowly("We'll use the Vercel CLI to log in with your GitHub account.");
  await printSlowly("This will open a browser window for you to authenticate.");
  
  try {
    await runCommand("npx vercel login");
    await printSlowly("Successfully logged in to Vercel with GitHub!");
    return true;
  } catch (error) {
    await printSlowly("Failed to log in to Vercel. Please try again.");
    return false;
  }
}

// Setup Stripe
async function setupStripe() {
  await printSlowly("Setting up Stripe...");
  const apiKey = await getInput("Enter your Stripe API Key: ");
  return apiKey;
}

// Deploy application
async function deployApplication() {
  await printSlowly("Deploying application to Vercel...");
  try {
    await runCommand("npx vercel --prod");
    await printSlowly("Application deployed successfully!");
  } catch (error) {
    await printSlowly("Deployment failed. Please check the logs.");
  }
}

// Main function
async function main() {
  console.clear();
  await printSlowly("Welcome to the Incident Management SaaS Setup CLI!");
  await printSlowly("This tool will guide you through the setup and deployment process.");

  const vercelSuccess = await setupVercel();

  if (!vercelSuccess) {
    await printSlowly("Failed to set up Vercel. Exiting setup.");
    rl.close();
    return;
  }

  const stripeApiKey = await setupStripe();

  // Save Stripe API key to .env file
  try {
    fs.writeFileSync('.env', `STRIPE_API_KEY=${stripeApiKey}\n`);
    await printSlowly("Stripe API key saved to .env file.");
  } catch (error) {
    console.error(`Error saving Stripe API key: ${error.message}`);
  }

  // Deploy the application
  await deployApplication();

  await printSlowly("Setup and deployment complete!");
  rl.close();
}

main();