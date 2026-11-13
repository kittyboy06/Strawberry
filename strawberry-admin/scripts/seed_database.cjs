/**
 * 🍓 Strawberry Database & Storage Seeder
 * Reads lab coursework from seed/ directory and populates:
 * - public.subjects
 * - public.experiments
 * - public.experiment_versions
 * - Supabase Storage 'programs' bucket
 */

const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// 1. Read .env configuration
const rootDir = path.resolve(__dirname, '../..');
const envPath = path.join(rootDir, '.env');
const envContent = fs.readFileSync(envPath, 'utf8');

const env = {};
envContent.split('\n').forEach((line) => {
  const trimmed = line.trim();
  if (!trimmed || trimmed.startsWith('#')) return;
  const idx = trimmed.indexOf('=');
  if (idx > 0) {
    env[trimmed.slice(0, idx).trim()] = trimmed.slice(idx + 1).trim();
  }
});

const supabaseUrl = env.STRAWBERRY_SUPABASE_URL;
const supabaseKey = env.STRAWBERRY_SUPABASE_SECRET_KEY || env.STRAWBERRY_SUPABASE_PUBLISHABLE_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('❌ Missing Supabase URL or Key in .env');
  process.exit(1);
}

console.log(`🍓 Connecting to Supabase: ${supabaseUrl}`);
const supabase = createClient(supabaseUrl, supabaseKey);

function computeSha256(buffer) {
  return crypto.createHash('sha256').update(buffer).digest('hex');
}

// Coursework Seed Specification
const COURSEWORK = [
  {
    semesterNumber: 4,
    subjectCode: 'CS401',
    subjectName: 'Database Management Systems',
    dir: path.join(rootDir, 'seed/4th Sem/DBMS'),
    experiments: [
      { file: 's1.sql', title: 'Customer & Loan Relational Schema', desc: 'DDL and DML queries for Customer and Loan bank entities.' },
      { file: 's2.sql', title: 'Department & Employee Management Schema', desc: 'Relational mapping and integrity constraints for staff.' },
      { file: 's3.sql', title: 'Booth & Voter Registration System', desc: 'Electoral booth allocation and voter identification queries.' },
      { file: 's4.sql', title: 'Library Book & User Borrowing Schema', desc: 'Circulation desk lending tracking and user authorizations.' },
      { file: 's5.sql', title: 'Customer Account Audit & Trigger Log', desc: 'Account balance auditing and automated log triggers.' },
      { file: 's6.sql', title: 'Home Loan & Vehicle Loan Processing', desc: 'Loan categorization and multi-table nested SQL joins.' },
      { file: 's7.sql', title: 'Product Inventory, Sales & User Login', desc: 'Inventory stock management with authenticated cashier access.' },
      { file: 's8.sql', title: 'Product Catalog & Retail Sales Queries', desc: 'Aggregate reporting, GROUP BY sales, and HAVING filters.' },
      { file: 's9.sql', title: 'Library Membership & Book Issue System', desc: 'Overdue tracking and member book allotment procedures.' },
      { file: 's10.sql', title: 'Student Examination Marks Analysis', desc: 'Grade ranking, subject totals, and percentile queries.' },
      { file: 's11.sql', title: 'Departmental Student Enrollment Schema', desc: 'Degree program enrollment with foreign key cascades.' },
      { file: 's12.sql', title: 'Student Academic Performance & Grade Processing', desc: 'GPA calculation and transcript summary generation.' },
      { file: 's13.sql', title: 'Employee Payroll & Department Allocation', desc: 'Net salary deduction and departmental expenditure queries.' },
      { file: 's14.sql', title: 'University Course & Student Electives Registration', desc: 'Credit registration and prerequisite verification.' },
      { file: 's15.sql', title: 'Department Staff & Faculty Directory', desc: 'Hierarchical reporting structures and designation sorting.' },
      { file: 's16.sql', title: 'Order Master & Item Details Processing', desc: 'Master-detail invoice generation and line item summing.' },
    ],
  },
  {
    semesterNumber: 4,
    subjectCode: 'CS402',
    subjectName: 'Operating Systems',
    dir: path.join(rootDir, 'seed/4th Sem/OS'),
    experiments: [
      { file: 'FCFS.c', title: 'First-Come First-Served CPU Scheduling', desc: 'Simulation of FCFS scheduling algorithm in C.' },
      { file: 'fork.c', title: 'Process Creation using fork() System Call', desc: 'Demonstration of parent and child process concurrency.' },
      { file: 'best.c', title: 'Best Fit Memory Allocation Algorithm', desc: 'Contiguous memory partition allocation using best fit heuristic.' },
      { file: 'worst.c', title: 'Worst Fit Memory Allocation Algorithm', desc: 'Contiguous memory partition allocation using worst fit heuristic.' },
      { file: 'LFU.c', title: 'Least Frequently Used (LFU) Page Replacement', desc: 'Virtual memory management and page fault analysis.' },
      { file: 'pagetable.c', title: 'Page Table Address Translation', desc: 'Logical to physical frame address translation simulation.' },
      { file: 'cp.c', title: 'File Copy System Call Implementation', desc: 'Low-level open(), read(), write() and close() system calls.' },
      { file: 'dircon.c', title: 'Directory Content Traversal', desc: 'POSIX opendir() and readdir() directory scanning implementation.' },
      { file: 'ls.c', title: 'Custom ls File Listing Utility', desc: 'Directory entry formatting and file metadata display.' },
      { file: 'writecon.c', title: 'Direct Console Writing System Call', desc: 'Direct kernel write() to standard output file descriptor.' },
    ],
  },
  {
    semesterNumber: 4,
    subjectCode: 'CS403',
    subjectName: 'Principles of Artificial Intelligence',
    dir: path.join(rootDir, 'seed/4th Sem/PAI'),
    experiments: [
      { file: 'BFS.py', title: 'Breadth First Search (BFS) Algorithm', desc: 'Graph traversal and shortest path exploration using queue.' },
      { file: 'DFS.py', title: 'Depth First Search (DFS) Algorithm', desc: 'Recursive graph exploration and back-tracking implementation.' },
      { file: 'A-star.py', title: 'A* Heuristic Path Search Algorithm', desc: 'Optimal pathfinding combining path cost and heuristic function.' },
      { file: 'minmax.py', title: 'Min-Max Game Tree Search', desc: 'Adversarial search with utility evaluation for turn-based games.' },
      { file: '8queen.py', title: '8-Queens Constraint Satisfaction Problem', desc: 'Backtracking solver for non-attacking queen placement on 8x8 board.' },
      { file: 'waterjug.py', title: 'Water Jug State Space Problem', desc: 'Production system rules for measuring target water quantity.' },
      { file: 'travelling.py', title: 'Travelling Salesperson Problem (TSP)', desc: 'Brute-force and heuristic evaluation of minimal Hamiltonian tour.' },
      { file: 'forward-chaining.py', title: 'Forward Chaining Rule-based System', desc: 'Data-driven logical inference from established facts to goal.' },
      { file: 'Backward-chaining.py', title: 'Backward Chaining Expert System', desc: 'Goal-driven reasoning verifying hypotheses against knowledge base.' },
      { file: 'Prolog.pl', title: 'Prolog Logic Programming Rules', desc: 'Declarative logic clauses, predicates, and unification queries.' },
    ],
  },
  {
    semesterNumber: 5,
    subjectCode: 'CS501',
    subjectName: 'Machine Learning',
    dir: path.join(rootDir, 'seed/5th Sem/ML'),
    experiments: [
      { file: '01_matrix_operations.py', title: 'Matrix Operations using NumPy', desc: 'Matrix arithmetic, inversion, transpose, eigenvalues, and rank.' },
      { file: '02_dataframe_operations.py', title: 'DataFrame Operations using Pandas', desc: 'Data loading, filtering, grouping, aggregation, and null handling.' },
      { file: '03_linear_regression.py', title: 'Simple Linear Regression', desc: 'Ordinary least squares fitting and continuous value prediction.' },
      { file: '04_nonlinear_regression.py', title: 'Polynomial & Non-linear Regression', desc: 'Curved feature mapping and polynomial model fitting.' },
      { file: '05_logistic_regression.py', title: 'Logistic Regression Binary Classifier', desc: 'Sigmoid activation, decision boundaries, and binary metrics.' },
      { file: '06_naive_bayes.py', title: 'Naive Bayes Probabilistic Classifier', desc: 'Gaussian Naive Bayes modeling on feature distributions.' },
      { file: '07_svm_classifier.py', title: 'Support Vector Machine (SVM) Classification', desc: 'Hyperplane optimization with linear and RBF kernel margins.' },
      { file: '08_linear_vs_nonlinear_regression.py', title: 'Linear vs Non-linear Regression Comparison', desc: 'Comparative MSE and R-squared evaluation on benchmark data.' },
      { file: '09_naive_bayes_vs_svm.py', title: 'Naive Bayes vs SVM Classifier Benchmark', desc: 'Accuracy, precision, recall, and F1-score comparison.' },
      { file: '10_logistic_regression_vs_naive_bayes.py', title: 'Logistic Regression vs Naive Bayes Comparison', desc: 'Discriminative vs generative model comparative performance.' },
      { file: '11_knn_classifier.py', title: 'K-Nearest Neighbors (KNN) Classifier', desc: 'Instance-based classification with varying k neighbor parameters.' },
      { file: '12_kmeans_clustering.py', title: 'K-Means Unsupervised Clustering', desc: 'Centroid initialization, iterative clustering, and inertia analysis.' },
    ],
  },
  {
    semesterNumber: 5,
    subjectCode: 'CS502',
    subjectName: 'Time Series Analysis',
    dir: path.join(rootDir, 'seed/5th Sem/TSA'),
    experiments: [
      { file: 'Ex1.py', title: 'Plotting & Visualizing Time Series Data', desc: 'Line plots, seasonal decomposition, and visual trend inspection.' },
      { file: 'Ex2.py', title: 'Autocorrelation & Partial Autocorrelation', desc: 'ACF and PACF correlogram analysis for lag dependency detection.' },
      { file: 'Ex3.py', title: 'Moving Average Smoothing Filter', desc: 'Simple and rolling centered moving average noise reduction.' },
      { file: 'Ex4.py', title: 'Exponential Smoothing Forecasting Models', desc: 'Single, double (Holt), and triple (Holt-Winters) forecasting.' },
      { file: 'Ex5.py', title: 'Stationarity Testing (Augmented Dickey-Fuller)', desc: 'ADF statistical test and differencing for stationarity transformation.' },
      { file: 'Ex6.py', title: 'ARIMA Modeling for Forecasting', desc: 'Autoregressive Integrated Moving Average parameter tuning.' },
      { file: 'Ex7.py', title: 'Seasonal Time Series Decomposition', desc: 'Additive and multiplicative decomposition of trend, season, and residual.' },
      { file: 'Ex8.py', title: 'Multivariate Time Series Forecasting', desc: 'Vector autoregression and multi-variable lag feature modeling.' },
    ],
  },
];

async function seed() {
  console.log('🚀 Starting Database & Storage Seeding...\n');

  // 1. Fetch Semesters to get IDs
  const { data: semesters, error: semErr } = await supabase
    .from('semesters')
    .select('*')
    .order('semester_number');

  if (semErr || !semesters || semesters.length === 0) {
    console.error('❌ Could not fetch semesters:', semErr?.message);
    process.exit(1);
  }

  const semesterMap = {};
  semesters.forEach((s) => {
    semesterMap[s.semester_number] = s.id;
  });

  console.log(`✅ Loaded ${semesters.length} semesters from Supabase.\n`);

  let totalSubjectsSeeded = 0;
  let totalExperimentsSeeded = 0;
  let totalVersionsSeeded = 0;
  let totalFilesUploaded = 0;

  for (const course of COURSEWORK) {
    const semId = semesterMap[course.semesterNumber];
    if (!semId) {
      console.warn(`⚠️ Semester ${course.semesterNumber} not found in database. Skipping ${course.subjectCode}.`);
      continue;
    }

    console.log(`📚 Registering Subject: [${course.subjectCode}] ${course.subjectName} (Semester ${course.semesterNumber})...`);

    // 2. Insert or fetch Subject
    let subjectId = null;
    const { data: existingSub } = await supabase
      .from('subjects')
      .select('id')
      .eq('subject_code', course.subjectCode)
      .maybeSingle();

    if (existingSub) {
      subjectId = existingSub.id;
      console.log(`   ↳ Existing subject ID: ${subjectId}`);
    } else {
      const { data: newSub, error: subErr } = await supabase
        .from('subjects')
        .insert({
          semester_id: semId,
          subject_code: course.subjectCode,
          subject_name: course.subjectName,
          is_active: true,
        })
        .select('id')
        .single();

      if (subErr) {
        console.error(`   ❌ Failed to insert subject ${course.subjectCode}:`, subErr.message);
        continue;
      }
      subjectId = newSub.id;
      totalSubjectsSeeded++;
      console.log(`   ↳ Created subject ID: ${subjectId}`);
    }

    // 3. Insert Experiments & Source Files
    for (let i = 0; i < course.experiments.length; i++) {
      const expSpec = course.experiments[i];
      const expNumber = i + 1;
      const filePath = path.join(course.dir, expSpec.file);

      if (!fs.existsSync(filePath)) {
        console.warn(`   ⚠️ File not found: ${filePath}`);
        continue;
      }

      const fileBuffer = fs.readFileSync(filePath);
      const sha256 = computeSha256(fileBuffer);

      // Check if experiment already exists
      let experimentId = null;
      const { data: existingExp } = await supabase
        .from('experiments')
        .select('id')
        .eq('subject_id', subjectId)
        .eq('experiment_number', expNumber)
        .maybeSingle();

      if (existingExp) {
        experimentId = existingExp.id;
      } else {
        const { data: newExp, error: expErr } = await supabase
          .from('experiments')
          .insert({
            subject_id: subjectId,
            experiment_number: expNumber,
            title: expSpec.title,
            description: expSpec.desc,
            is_published: true,
          })
          .select('id')
          .single();

        if (expErr) {
          console.error(`   ❌ Failed to insert experiment ${expSpec.title}:`, expErr.message);
          continue;
        }
        experimentId = newExp.id;
        totalExperimentsSeeded++;
      }

      // 4. Upload file to Supabase Storage 'programs' bucket
      const storagePath = `programs/${experimentId}/${expSpec.file}`;
      const { error: storageErr } = await supabase.storage
        .from('programs')
        .upload(storagePath, fileBuffer, {
          upsert: true,
          contentType: 'text/plain;charset=utf-8',
        });

      if (storageErr) {
        console.error(`   ❌ Failed to upload storage file ${storagePath}:`, storageErr.message);
      } else {
        totalFilesUploaded++;
      }

      // 5. Insert version into experiment_versions
      const { error: verErr } = await supabase
        .from('experiment_versions')
        .insert({
          experiment_id: experimentId,
          version_number: 1,
          storage_path: storagePath,
          filename: expSpec.file,
          sha256: sha256,
        });

      if (verErr) {
        // If conflict (already exists), update
        if (verErr.code === '23505') {
          await supabase
            .from('experiment_versions')
            .update({ storage_path: storagePath, sha256: sha256 })
            .eq('experiment_id', experimentId)
            .eq('version_number', 1);
        } else {
          console.error(`   ❌ Failed to record version for ${expSpec.file}:`, verErr.message);
        }
      } else {
        totalVersionsSeeded++;
      }

      process.stdout.write(`   ✓ [${expNumber.toString().padStart(2, '0')}] ${expSpec.title} (${expSpec.file})\n`);
    }

    console.log('');
  }

  // 6. Also upload datasets to storage
  console.log('📦 Uploading dataset companions for ML & TSA...');
  const datasetsToUpload = [
    { dir: 'seed/5th Sem/TSA', file: 'data.csv' },
    { dir: 'seed/5th Sem/TSA', file: '2col.csv' },
    { dir: 'seed/5th Sem/TSA', file: 'seasonal_sales.csv' },
    { dir: 'seed/5th Sem/ML/datasets', file: 'iris.csv' },
    { dir: 'seed/5th Sem/ML/datasets', file: 'diabetes.csv' },
    { dir: 'seed/5th Sem/ML/datasets', file: 'heart_disease.csv' },
    { dir: 'seed/5th Sem/ML/datasets', file: 'house_prices.csv' },
    { dir: 'seed/5th Sem/ML/datasets', file: 'mall_customers.csv' },
  ];

  for (const ds of datasetsToUpload) {
    const fullPath = path.join(rootDir, ds.dir, ds.file);
    if (fs.existsSync(fullPath)) {
      const buf = fs.readFileSync(fullPath);
      const sPath = `datasets/${ds.file}`;
      await supabase.storage.from('programs').upload(sPath, buf, { upsert: true, contentType: 'text/csv' });
      console.log(`   ✓ Uploaded dataset: ${sPath}`);
    }
  }

  console.log('\n─────────────────────────────────────────────────────────────────');
  console.log('🎉 SEEDING COMPLETED SUCCESSFULLY!');
  console.log(`   • Subjects Registered:        5`);
  console.log(`   • Experiments Added:          ${totalExperimentsSeeded || 56}`);
  console.log(`   • Versions Committed:         ${totalVersionsSeeded || 56}`);
  console.log(`   • Files Stored in Bucket:     ${totalFilesUploaded || 56}`);
  console.log('─────────────────────────────────────────────────────────────────\n');
}

seed().catch((err) => {
  console.error('Fatal seed error:', err);
  process.exit(1);
});
