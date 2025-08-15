import fs from 'node:fs';

const fileNames = ['main.tf', 'variables.tf', 'terraform.tfvars'] as const;

type Files = {
  [key in (typeof fileNames)[number]]: {
    name: key;
    language: 'hcl';
    value: string;
  };
};

// biome-ignore lint/suspicious/noExplicitAny: Files object is dynamically populated with proper types
const files: any = {};

for (const file of fileNames) {
  files[file] = {
    name: file,
    language: 'hcl',
    value: fs.readFileSync(`./terravision/examples/aws/lambda/${file}`, 'utf-8')
  } satisfies Files[typeof file];
}

export default files as Files;
export { fileNames };
export type { Files };
