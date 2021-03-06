/******************************************************************************

Copyright (c) 2013, Mandar Chitre

This file is part of fjage which is released under Simplified BSD License.
See file LICENSE.txt or go to http://www.opensource.org/licenses/BSD-3-Clause
for full license details.

******************************************************************************/

package org.arl.fjage.shell;

import org.arl.fjage.Message;

/**
 * An interface for a client interested in monitoring messages in the shell.
 *
 * @author  Mandar Chitre
 */
public interface MessageListener {

  /**
   * This method is called for each message to be conveyed to the listener.
   *
   * @param msg received message.
   */
  public void onReceive(Message msg);

}
