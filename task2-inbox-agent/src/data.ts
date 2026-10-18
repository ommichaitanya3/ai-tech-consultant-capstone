import type { EmailRecord } from "./types.js";
const seeds = [
 ["How do I change my website logo?","How-to question","low","Use sources for instructions."],
 ["My payment integration stopped working.","Troubleshooting","medium","Retrieve evidence; escalate if unsupported."],
 ["Can you add a custom booking feature?","Project request","high","Do not promise delivery."],
 ["Please refund last month's invoice.","Refund or cancellation","high","Never approve refund automatically."],
 ["Your update broke our website.","Complaint","high","Acknowledge and route to human."],
 ["Can you quote an integration?","Quote request","high","Do not invent price or timeline."],
 ["Did you receive my previous request?","Follow-up","medium","Ask for context if unavailable."]
] as const;
export const emails:EmailRecord[]=Array.from({length:50},(_,i)=>{
 const seed=seeds[i%seeds.length];
 return {id:`EMAIL-${String(i+1).padStart(3,"0")}`,subject:seed[0],from:`customer${i+1}@example.test`,
 body:seed[0]+(i<7?"":` (synthetic example ${i+1}; please advise on the next step)`),
 category:seed[1],risk:seed[2],expectedBehavior:seed[3]};
});
