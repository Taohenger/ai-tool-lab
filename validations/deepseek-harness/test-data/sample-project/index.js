// task-003 headless 与 task-008 代码编辑测试用的小工具
export function greet(name = "world") {
  return `Hello, ${name}!`;
}

export function add(a, b) {
  return a + b;
}

export function fibonacci(n) {
  if (n < 2) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

if (require.main === module) {
  // $ node index.js Bob
  const who = process.argv[2];
  console.log(greet(who));
  console.log("fib(10) =", fibonacci(10));
}
