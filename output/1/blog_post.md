# Reclaiming Your Digital Sovereignty: Why Programmatic Cloud Backups Are Non-Negotiable

My journey into the world of backups began in the trenches of early Linux operating systems. Back in school, I learned a crucial lesson the hard way: after repeatedly breaking my OS, the **importance of backups became undeniable**. Fast forward to today, and while my need to back up local operating systems has diminished, the imperative to back up cloud resources has only grown more urgent and pressing.

For many, the very idea of "backing up the cloud" might seem nonsensical, even provoke a bit of a stir. I might be in the minority, but my philosophy towards cloud computing is largely positive, with one critical caveat: I believe in the **fundamental right to periodically back up my own data**. I view this as an unalienable right of digital sovereignty, and the current norm, where this is often treated as a luxury, is, to my mind, perverse.

## The Cloud Backup Conundrum: A Digital Sovereignty Imperative

As cloud computing solidifies its position as the primary way for most computer users – both consumers and businesses – to store their data, the number of services this data might be spread across continues to grow exponentially. This proliferation makes robust backup strategies more critical than ever.

## The Power of Programmatic Backups

For any backup to be truly effective, it needs to be **programmatic**. Some would even argue that only programmatic backups hold any real utility, a viewpoint I wholeheartedly agree with. Manual backups are prone to human error, inconsistency, and are simply not scalable in our increasingly data-rich environments.

Unfortunately, by this standard, the number of providers offering consumers reliable means to programmatically back up their data from cloud applications is disappointingly small.

### GitHub: A Gold Standard

An excellent example of a provider that gets it right is GitHub. They offer a capable API that users can leverage to script their own backups. While commercial GitHub backup providers certainly exist, the availability of a robust API empowers any user to create custom backup solutions. This capability is more valuable than ever, especially with the proliferation of AI tools making scripting more accessible.

However, GitHub remains the exception rather than the rule. Large segments of the cloud remain virtually impossible to back up programmatically.

## Why Most Cloud Providers Fall Short

Over the years, backup approaches offered by cloud providers have slowly begun to change. The advent of data liberation frameworks, such as GDPR, has put pressure on tech vendors to provide at least some rudimentary backup mechanisms to consumers. Yet, even when implemented, these often fall far short of the desired degree of user-friendliness and comprehensive functionality for effective backup operations.

> "The amount of providers which offer consumers reliable means to programmatically back up their data, sorting their cloud applications is disappointingly small."

Take Hashnode, a popular blogging service for tech writers and developers. They offer some backup mechanisms, but as is very commonly the case, their exports often **don't include CDN images**. This means scripting is still needed to achieve a complete backup. It highlights a recurring theme: providers offer *some* solution, but rarely a *complete* or *programmatic* one.

## My Approach: A New Repository for Cloud Backup Strategies

I previously maintained a GitHub repository with notes on backing up various cloud tools. However, that repository hasn't been updated in over five years. Rather than going through the tedious process of updating individual, outdated notes, I decided it made more sense to **start afresh**. This new initiative accounts for the significant rise of AI tools and other developments in cloud computing since the last update.

I plan to periodically update this new repository with notes, organizing services into folders and data types within those service folders. For each service, I'll aim to detail:

-   What defaults or built-in mechanisms providers offer.
-   What third-party tools exist.
-   Links to any custom scripts I've created for backups.
-   Any other useful utilities found on GitHub for backing up these tools.

It would be almost impossible to capture even a reasonable percentage of the cloud services consumers use and whose data they might wish to back up. Therefore, **contributions are warmly welcome** within the spirit of this objective!

## Why Back Up the Cloud? Beyond Vendor Lock-in

The common misconception is that "the cloud *is* the backup." This is fundamentally untrue. Besides critical digital federacy concerns and data security, I've personally witnessed countless instances where users lose access to their cloud data. These range from:

-   **Vendor lockouts:** Losing access due to policy changes or account issues.
-   **Rapid shifts in affordability:** Services becoming unexpectedly expensive, forcing users to migrate or lose data.
-   **Ransomware propagation:** Cloud storage is not immune to malicious attacks.

There are plenty of compelling reasons why it's simply prudent to keep a backup of any data you depend upon, regardless of whether it's stored locally or in the cloud.

## Embracing the 3-2-1 Rule for Cloud Data

The basic backup best practice of the **3-2-1 rule** remains an excellent starting point, even for cloud data. This means keeping:

-   **3 copies** of your data.
-   On **2 different media types**.
-   With **1 copy off-site**.

Applied to cloud data, this translates to keeping two additional copies of your cloud data: one in an on-site location (your local environment) and another in a *different* cloud.

For instance, using GitHub as our example (given its robust API):

1.  You could script an **incremental backup** of your repositories to a local NAS (Network Attached Storage).
2.  Then, sync that NAS up to an S3 bucket or a B2 bucket.

This strategy provides you with two additional copies beyond GitHub itself, adhering to the 3-2-1 principle. GitHub, with its robust API, serves as a **gold standard** for the type of data backup capabilities that I believe should be the norm for all cloud providers.

## Conclusion

The need for programmatic cloud backups is not just a technical preference; it's a fundamental aspect of **digital sovereignty** in an increasingly cloud-centric world. While many providers still fall short, the path forward involves advocating for better APIs, leveraging tools like AI for scripting, and taking personal responsibility for our data through robust strategies like the 3-2-1 rule. My new repository aims to be a valuable resource in this ongoing effort to empower users and ensure our data remains truly our own.