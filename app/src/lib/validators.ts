import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import { graphSchema, ProjectGraph } from './schemas';

const ajv = new Ajv({ allErrors: true, strict: true });
addFormats(ajv);
const validate = ajv.compile(graphSchema);

export class ValidationError extends Error {
  constructor(public readonly issues: string[]) {
    super(`Project validation failed: ${issues.join('; ')}`);
  }
}

export const validateProject = (project: ProjectGraph) => {
  const valid = validate(project);
  if (!valid) {
    const issues = (validate.errors ?? []).map((error) => `${error.instancePath || '/'} ${error.message ?? ''}`.trim());
    throw new ValidationError(issues);
  }
  return project;
};
