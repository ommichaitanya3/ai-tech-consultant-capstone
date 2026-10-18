export type Risk = "low" | "medium" | "high";
export type EmailRecord = {id:string;subject:string;from:string;body:string;category:string;risk:Risk;expectedBehavior:string};
export type KnowledgeSource = {title:string;url:string;excerpt:string;relevance:number};
export type DraftResult = {emailId:string;category:string;risk:Risk;summary:string;draft:string;sources:KnowledgeSource[];needsHuman:boolean;status:"draft"|"insufficient_evidence"};
